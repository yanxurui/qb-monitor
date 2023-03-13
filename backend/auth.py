from aiohttp_security.abc import AbstractAuthorizationPolicy

class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, user_map):
        super().__init__()
        self.user_map = user_map

    async def authorized_userid(self, identity: str):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        return self.user_map.get(identity)

    async def permits(self, identity, permission, context=None):
        pass
