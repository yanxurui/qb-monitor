from aiohttp_security.abc import AbstractAuthorizationPolicy

from user import User

class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity: str):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        return await User.get(token=identity)

    async def permits(self, identity, permission, context=None):
        pass
