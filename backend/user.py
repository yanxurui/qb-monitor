import datetime
import logging
import json
import os
from uuid import uuid4

import sqlite3
import aiosqlite
from cachetools import TTLCache


class User:
    '''User class'''
    # create conf_folder if it does not exist
    conf_folder = 'conf'
    if not os.path.exists(conf_folder):
        os.makedirs(conf_folder)

    # create the table if it does not exist
    db_path = 'sqlite.db'
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY, userid TEXT UNIQUE, token TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

    user_cache = TTLCache(maxsize=1024, ttl=60*60*24)

    def __init__(self, userid, token=None, created_at=None):
        self.userid = userid
        self.token = token
        self.created_at = created_at
        self.config = None
        c = self.readConfig()
        if c is not None:
            config = json.loads(c)
            self.config = config

    async def create(self):
        '''save user to db'''
        self.token = str(uuid4())
        self.created_at = datetime.datetime.now()
        async with aiosqlite.connect(User.db_path) as conn:
            await conn.execute(
                'INSERT INTO users (userid, token, created_at) VALUES (?, ?, ?)',
                (self.userid, self.token, self.created_at))
            await conn.commit()

    async def renew_token(self):
        '''renew token'''
        del User.user_cache[self.token]
        self.token = str(uuid4())
        async with aiosqlite.connect(User.db_path) as conn:
            await conn.execute(
                'UPDATE users SET token=? WHERE userid=?',
                (self.token, self.userid))
            await conn.commit()

    def getPath(self):
        return os.path.join(self.conf_folder, self.userid + '.json')

    def readConfig(self):
        path = self.getPath()
        try:
            with open(path) as f:
                return f.read()
        except Exception as e:
            logging.exception(e)
            return None

    @classmethod
    async def get(cls, userid=None, token=None):
        '''get user by userid or token'''
        if userid is not None:
            async with aiosqlite.connect(cls.db_path) as conn:
                async with conn.execute('SELECT * FROM users WHERE userid=?', (userid,)) as cursor:
                    row = await cursor.fetchone()
        elif token is not None:
            user = cls.user_cache.get(token)
            if user is not None:
                logging.info('User retrieved from cache')
                return user
            async with aiosqlite.connect(User.db_path) as conn:
                async with conn.execute('SELECT * FROM users WHERE token=?', (token,)) as cursor:
                    row = await cursor.fetchone()
        if row:
            user = User(row[1], row[2], row[3])
            cls.user_cache[token] = user
            return user
        return None

    @staticmethod
    async def signin(userid):
        '''signup a new user'''
        user = await User.get(userid)
        if user:
            return user, 200
        else:
            user = User(userid)
            await user.create()
            return user, 201
