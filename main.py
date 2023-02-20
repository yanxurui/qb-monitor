"""Route declaration."""

import time
import logging
import asyncio
from importlib import reload
from datetime import datetime

import httpx
from flask import Flask
from flask import render_template

import conf

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
    level=logging.INFO)

app = Flask(__name__)


@app.route('/')
async def home():
    start = time.time()
    app.logger.info('Started')
    global conf
    conf = reload(conf)
    qb_info = await get_info_all(conf.qbs)
    end = time.time()
    duration = end - start
    app.logger.info('Finishied in {0:.2f} seconds'.format(duration))

    return render_template(
        'home.html',
        qb_info=qb_info,
        duration=duration,
        now=datetime.now().strftime("%H:%M:%S"))

async def get_info_all(qbs):
    tasks = [query_qb_with_retry(qb) for qb in qbs]
    result = await asyncio.gather(*tasks)
    return qbs

async def query_qb_with_retry(qb):
    url = qb['url']
    retry_count = 3
    while retry_count > 0:
        if retry_count < 3:
            app.logger.info("let's retry")
        try:
            return await query_qb(qb)
        except httpx.ReadError:
            app.logger.exception('Failed to request {}'.format(url))
            retry_count = retry_count - 1
        except:
            app.logger.exception('Failed to process {}'.format(url))
            return False

async def query_qb(qb):
    url = qb['url']
    app.logger.info('Requesting {}'.format(url))
    start = time.time()
    async with httpx.AsyncClient(timeout=4) as s:
        r = await s.post(url+'/api/v2/auth/login', data={
            'username': qb['username'],
            'password': qb['password']
            })

        if r.status_code != 200:
            app.logger.error('failed to login {}'.format(url))
            return False
        end = time.time()
        app.logger.info('Login {0} in {1:.2f} seconds'.format(url, end-start))

        r = await s.get(url+'/api/v2/transfer/info')
        if r.status_code != 200:
            app.logger.error('failed to get transfer info {}'.format(url))
            return True
        j = r.json()
        qb['dl_info_speed'] = sizeof_fmt(j['dl_info_speed'])
        qb['dl_info_data'] = sizeof_fmt(j['dl_info_data'])
        qb['up_info_speed'] = sizeof_fmt(j['up_info_speed'])
        qb['up_info_data'] = sizeof_fmt(j['up_info_data'])
        end = time.time()
        app.logger.info('Finished {0} in {1:.2f} seconds'.format(url, end-start))
        return True


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
