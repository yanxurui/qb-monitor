import datetime
import logging

import sqlite3
import aiosqlite
from uuid import uuid4

class UserTable:
    '''User table
    A singleton class to manage user table
    '''
    db_path = 'sqlite.db'
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, uuid TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

    @classmethod
    async def insert(cls, username, password):
        '''create a new user'''
        async with aiosqlite.connect(cls.db_path) as conn:
            await conn.execute(
                'INSERT INTO users (username, password, uuid, created_at) VALUES (?, ?, ?, ?)',
                (username, password, str(uuid4()), datetime.datetime.now()))
            await conn.commit()

    @classmethod
    async def update(cls, username, password):
        '''update the user info by username'''
        async with aiosqlite.connect(cls.db_path) as conn:
            await conn.execute(
                'UPDATE users SET password=?, uuid=? WHERE username=?',
                (password, str(uuid4()), username))
            await conn.commit()

    @classmethod
    async def get(cls, username):
        '''get user info by username'''
        async with aiosqlite.connect(cls.db_path) as conn:
            async with conn.execute('SELECT * FROM users WHERE username=?', (username,)) as cursor:
                return await cursor.fetchone()


class User:
    '''User class'''
    def __init__(self, username, password, uuid=None, created_at=None):
        self.username = username
        self.password = password
        self.uuid = uuid
        self.created_at = created_at
        self.config = None

    async def create(self):
        '''save user to db'''
        await UserTable.insert(self.username, self.password)

    async def udpate(self, new_password):
        '''update user info'''
        await UserTable.update(self.username, new_password)

    @staticmethod
    async def get(username):
        '''get user by username'''
        row = await UserTable.get(username)
        if row:
            return User(row[1], row[2], row[3], row[4])
        return None
