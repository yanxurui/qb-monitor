import os
import errno
import json
import time
import logging
from datetime import datetime

import sqlite3
import aiohttp
from aiohttp import web
from aiohttp_security import CookiesIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_security import remember, forget, check_authorized

from user import User
from auth import DictionaryAuthorizationPolicy

user_map = {}

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
    level=logging.INFO)
routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    directory = request.app.router['static'].get_info()['directory']
    location = os.path.join(directory, 'index.html')
    return web.FileResponse(path=location)

@routes.post('/register')
async def register(request):
    data = await request.json()
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        raise web.HTTPBadRequest(text='username or password should not be null')
    user = User(username, password)
    try:
        await user.create()
    except sqlite3.IntegrityError as e:
        app.logger.exception(e)
        raise web.HTTPBadRequest(text='Username already exists')
    # redirect internally
    return await login(request)

@routes.post('/login')
async def login(request):
    data = await request.json()
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        raise web.HTTPBadRequest(text='username or password should not be null')
    user = await User.get(username)
    if user and user.password == password:
        resp = web.Response(text='ok')
        # generate a uuid
        # Todo: memory leak caused by inactive user
        # Todo: when do we change the uuid?
        # Todo: what if the service restarts? User needs to login again
        user_map[user.uuid] = user
        await remember(request, resp, user.uuid)
        return resp
    else:
        if user is None:
            raise aiohttp.web.HTTPUnauthorized(text='User does not exist')
        else:
            raise aiohttp.web.HTTPUnauthorized(text='Wrong password')

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
    if config is None:
        c = ConfigView.readConfig(user.username)
        if c is None:
            raise web.HTTPNotFound()
        config = json.loads(c)
        user.config = config
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
    folder = 'conf'
    @classmethod
    def getPath(cls, username):
        return os.path.join(cls.folder, username + '.json')

    @classmethod
    def readConfig(cls, username):
        path = cls.getPath(username)
        try:
            with open(path) as f:
                return f.read()
        except Exception as e:
            logging.exception(e)
            return None

    async def get(self):
        user = await check_authorized(self.request)
        c = ConfigView.readConfig(user.username)
        if c:
            return web.Response(text=c)
        else:
            raise web.HTTPNotFound(text='No config')

    async def post(self):
        user = await check_authorized(self.request)
        data = await self.request.text()
        path = self.getPath(user.username)
        if not data.strip():
            # scenario 1: clean the config
            try:
                os.remove(path)
            except OSError as e:
                if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                    raise # re-raise exception if a different error occurred
            return web.Response(text='Deleted successfully!')

        # scenario 2: overwrite the existing config file
        try:
            config = json.loads(data)
        except Exception as e:
            app.logger.exception(e)
            raise web.HTTPBadRequest(text='Invalid json: ' + str(e))
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
setup_security(app, CookiesIdentityPolicy(), DictionaryAuthorizationPolicy(user_map))

if __name__ == '__main__':
    web.run_app(app, port=5001)
