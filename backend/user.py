import datetime
from uuid import uuid4

import sqlite3
import aiosqlite


class User:
    '''User class'''
    db_path = 'sqlite.db'
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY, userid TEXT UNIQUE, token TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

    def __init__(self, userid, token=None, created_at=None):
        self.userid = userid
        self.token = token
        self.created_at = created_at
        self.config = None

    async def create(self):
        '''save user to db'''
        self.token = str(uuid4())
        self.created_at = datetime.datetime.now()
        async with aiosqlite.connect(User.db_path) as conn:
            await conn.execute(
                'INSERT INTO users (userid, token, created_at) VALUES (?, ?, ?)',
                (self.userid, self.token, self.created_at))
            await conn.commit()

    async def update(self):
        async with aiosqlite.connect(User.db_path) as conn:
            await conn.execute(
                'UPDATE users SET token=? WHERE userid=?',
                (str(uuid4()), self.userid))
            await conn.commit()

    @classmethod
    async def get(cls, userid):
        '''get user by userid'''
        async with aiosqlite.connect(cls.db_path) as conn:
            async with conn.execute('SELECT * FROM users WHERE userid=?', (userid,)) as cursor:
                row = await cursor.fetchone()
        if row:
            return User(row[1], row[2], row[3])
        return None

    @staticmethod
    async def signin(userid):
        '''signup a new user'''
        user = await User.get(userid)
        if user:
            return user, 200
        else:
            await user.create()
            return user, 201
