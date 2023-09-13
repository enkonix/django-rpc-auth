from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import AuthenticationMiddleware as _AuthenticationMiddleware
from channels.auth import AuthMiddleware as _ChannelsAuthMiddleware
from channels.sessions import CookieMiddleware, SessionMiddleware
from channels.db import database_sync_to_async

from .helpers import GetUserHelper

session_cookie_name = settings.SESSION_COOKIE_NAME


class AuthenticationMiddleware(_AuthenticationMiddleware):
    def _get_user(self, request):
        session_id = request.COOKIES.get(session_cookie_name)
        user = GetUserHelper.get_user(session_id)
        return user

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        request.user = SimpleLazyObject(lambda: self._get_user(request))


class ChannelsAuthMiddleware(_ChannelsAuthMiddleware):
    @database_sync_to_async
    def _get_user(self, scope):
        session_id = scope.get('cookies', {}).get(session_cookie_name)
        user = GetUserHelper.get_user(session_id)
        return user

    async def resolve_scope(self, scope):
        # noinspection PyProtectedMember
        scope["user"]._wrapped = await self._get_user(scope)


ChannelsAuthMiddlewareStack = lambda inner: CookieMiddleware(SessionMiddleware(ChannelsAuthMiddleware(inner)))
