import os
import errno
import json
import time
import logging
from datetime import datetime

import aiohttp
from aiohttp import web
from aiohttp_security import CookiesIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_security import remember, forget, check_authorized

from google.oauth2 import _id_token_async
from google.auth.transport import _aiohttp_requests
from aiohttp_client_cache import CachedSession, CacheBackend

from user import User
from auth import DictionaryAuthorizationPolicy

request_cache = CacheBackend(expire_after=60*60)

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
    level=logging.INFO)
routes = web.RouteTableDef()

@routes.post('/signin')
async def signin(request):
    token = await request.text()
    try:
        async with CachedSession(cache=request_cache, auto_decompress=False) as cached_session:
            google_request = _aiohttp_requests.Request(session=cached_session)
            id_info = await _id_token_async.verify_oauth2_token(
                token,
                google_request,
                '582570402124-u6ntuo1s4ct7p83q2g33dd3ujtimpi4s.apps.googleusercontent.com')
    except ValueError as e:
        app.logger.exception(e)
        raise web.HTTPBadRequest(text='Invalid token')
    userid = id_info['sub']
    user, status = await User.signin(userid)
    resp = web.Response(text='ok', status=status)
    # memory leak caused by inactive user? use a TTL cache
    # when do we change the token? when the user logout all devices
    # user needs to login again when the service restarts? persist the token
    await remember(request, resp, user.token)
    return resp

@routes.post('/logout')
async def logout(request):
    await check_authorized(request)
    resp = web.Response(text='ok')
    await forget(request, resp)
    return resp

@routes.get('/qbs')
async def home(request):
    user = await check_authorized(request)
    config = user.config
    if not config:
        raise web.HTTPNotFound(text='No config')
    return web.json_response(config)

@routes.get(r'/qbs/{qb_id:\d+}')
async def get_qb_stats(request):
    user = await check_authorized(request)
    try:
        qb_id = int(request.match_info['qb_id'])
        qb = user.config[qb_id]
        qb['url'] = qb['url'].rstrip('/')
    except IndexError:
        raise aiohttp.web.HTTPBadRequest(text='Invalid qb_id')
    if not await query_qb_with_retry(qb):
        # if we failed to get the latest info
        # keep the total but remove the speed we got last time
        qb.pop('dl_info_speed', None)
        qb.pop('up_info_speed', None)
    return web.json_response(qb)

async def query_qb_with_retry(qb):
    url = qb['url']
    retry_count = 3
    while retry_count > 0:
        if retry_count < 3:
            app.logger.info("Let's retry")
        try:
            return await query_qb(qb)
        # except httpx.ReadError:
        #     app.logger.exception('Failed to request {}'.format(url))
        #     retry_count = retry_count - 1
        except:
            app.logger.exception('Failed to process {}'.format(url))
            return False

async def query_qb(qb):
    url = qb['url']
    app.logger.info('Requesting {}'.format(url))
    start = time.time()
    # It's important to set unsafe of CookieJar
    # otherwise, the default CookieJar won't update the cookies if the host is ip
    session_timeout = aiohttp.ClientTimeout(total=None,sock_connect=3,sock_read=3)
    async with aiohttp.ClientSession(timeout=session_timeout, cookie_jar=aiohttp.CookieJar(unsafe=True)) as s:
        async with s.post(url+'/api/v2/auth/login', data={
            'username': qb['username'],
            'password': qb['password']
            }) as r:

            if r.status != 200:
                app.logger.error('failed to login {}. Status code is {}'.format(url, r.status))
                return False
            end = time.time()
            app.logger.info('Login {0} in {1:.2f} seconds'.format(url, end-start))

        async with s.get(url+'/api/v2/transfer/info') as r:
            if r.status != 200:
                app.logger.error('failed to get transfer info {}. Status code is {}'.format(url, r.status))
                return False
            j = await r.json()
            qb['dl_info_speed'] = j['dl_info_speed']
            qb['dl_info_data'] = j['dl_info_data']
            qb['up_info_speed'] = j['up_info_speed']
            qb['up_info_data'] = j['up_info_data']
            end = time.time()
            app.logger.info('Finished {0} in {1:.2f} seconds'.format(url, end-start))
            return True

@routes.view('/config')
class ConfigView(web.View):
    async def get(self):
        user = await check_authorized(self.request)
        c = user.readConfig()
        if c:
            return web.Response(text=c)
        else:
            raise web.HTTPNotFound(text='No config')

    async def post(self):
        user = await check_authorized(self.request)
        data = await self.request.text()
        path = user.getPath()
        # scenario 1: clean the config
        if not data.strip():
            try:
                os.remove(path)
                user.config = None
            except OSError as e:
                if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                    raise # re-raise exception if a different error occurred
            return web.Response(text='Deleted successfully!')

        # validate the config
        try:
            config = json.loads(data)
            if type(config) is not list:
                raise ValueError('not a list')
            for qb in config:
                if type(qb) is not dict:
                    raise ValueError('not a dict')
                for required_key in ['name', 'url', 'username', 'password']:
                    if required_key not in qb:
                        raise ValueError('missing key: ' + required_key)
        except Exception as e:
            app.logger.exception(e)
            raise web.HTTPBadRequest(text='Invalid config: ' + str(e))

        # scenario 2: overwrite the existing config file
        try:
            with open(path, 'w') as f:
                f.write(data)
            user.config = config
        except Exception as e:
            logging.exception(e)
            raise web.HTTPInternalServerError(text='Failed to save the config file')
        return web.Response(text='Saved successfully!')


app = web.Application()
app.add_routes(routes)
setup_security(app, CookiesIdentityPolicy(), DictionaryAuthorizationPolicy())

if __name__ == '__main__':
    web.run_app(app, port=5001)
