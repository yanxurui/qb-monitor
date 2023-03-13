import os
import logging

from aiohttp import web
from aiohttp_security import check_authorized

class ConfigView(web.View):
    @staticmethod
    def readConfig(path):
        try:
            with open(path) as f:
                return f.read()
        except:
            logging.exception()
            return None

    def getPath(self, username):
        return os.path.join('config', username + '.json')

    async def get(self):
        user = await check_authorized(self.request)
        c = ConfigView.getConfig(self.getPath(user.username))
        if c:
            return web.Response(text=c)
        else:
            return web.HTTPNotFound(text='No config')

    async def post(self):
        user = await check_authorized(self.request)
        data = await self.request.post()
        path = self.getPath(user.username)
        try:
            with open(path, 'w') as f:
                return f.write(data)
        except Exception as e:
            logging.exception()
            return web.HTTPInternalServerError(text='Failed to save the config file')
        return web.Response(text='Saved successfully!')

