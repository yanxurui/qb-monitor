import os
import time
import logging
from datetime import datetime

import jinja2
import aiohttp_jinja2
import aiohttp
from aiohttp import web

from config import Config
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
    level=logging.INFO)
routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    directory = request.app.router['static'].get_info()['directory']
    location = os.path.join(directory, 'index.html')
    return web.FileResponse(path=location)

@routes.get('/qbs')
async def home(request):
    # reload config if necessary
    config = Config.get_config(update=True)
    return web.json_response(config['qbs'])

@routes.get(r'/qbs/{qb_id:\d+}')
async def get_qb_stats(request):
    try:
        qb_id = int(request.match_info['qb_id'])
        config = Config.get_config()
        qb = config['qbs'][qb_id]
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

app = web.Application()
app.add_routes(routes)
app.router.add_static('/', path='static', name='static')
aiohttp_jinja2.setup(app,
    loader=jinja2.FileSystemLoader('templates'))

if __name__ == '__main__':
    web.run_app(app, port=5001)

