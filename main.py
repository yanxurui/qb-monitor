"""Route declaration."""

import time
import logging
import functools
from importlib import reload
from datetime import datetime

import requests
import gevent
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask import render_template

import conf

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route('/')
def home():
    start = time.time()
    app.logger.info('Started')
    global conf
    conf = reload(conf)
    qb_info = get_info_all(conf.qbs)
    end = time.time()
    duration = end - start
    app.logger.info('Finishied in {0:.2f} seconds'.format(duration))

    return render_template(
        'home.html',
        qb_info=qb_info,
        duration=duration,
        now=datetime.now)

def get_info_all(qbs):
    pool = Pool(10)
    for ok in pool.imap_unordered(query_qb, qbs):
        pass
    return qbs

def query_qb(qb):
    retry_count = 3
    while retry_count > 0:
        if retry_count < 3:
            app.logger.info("let's retry")

        try:
            url = qb['url']
            app.logger.info('Requesting {}'.format(url))
            start = time.time()
            s = requests.Session()
            s.request = functools.partial(s.request, timeout=3)
            r = s.post(url+'/api/v2/auth/login', data={
                'username': qb['username'],
                'password': qb['password']
                })

            if r.status_code != 200:
                app.logger.error('failed to login {}'.format(url))
                return False
            r = s.get(url+'/api/v2/transfer/info')
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
        except requests.exceptions.ConnectionError:
            app.logger.exception('Failed to request {}'.format(url))
            retry_count = retry_count - 1
            continue
        except Exception:
            app.logger.exception('Failed to process {}'.format(url))
            return False

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

if __name__ == '__main__':
    app.run(debug=True)
