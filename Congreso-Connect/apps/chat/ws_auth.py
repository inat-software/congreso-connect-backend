"""
Autenticacion de WebSocket por JWT (SimpleJWT).

Los navegadores no pueden enviar el header `Authorization` al abrir un
WebSocket, asi que el token de acceso viaja como query param: `?token=<access>`.
Este middleware lo valida y resuelve `scope['user']` (o AnonymousUser).
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def _get_user(token):
    # Importes diferidos: este modulo se carga antes de que Django termine de
    # inicializar las apps (lo importa el ASGI), por eso no se importan arriba.
    from rest_framework_simplejwt.exceptions import TokenError
    from rest_framework_simplejwt.tokens import AccessToken

    try:
        access = AccessToken(token)          # valida firma y expiracion
        user_id = access['user_id']          # USER_ID_CLAIM del proyecto
    except (TokenError, KeyError):
        return AnonymousUser()

    User = get_user_model()
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Resuelve scope['user'] a partir del `?token=` del WebSocket."""

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get('query_string', b'').decode())
        token = (query.get('token') or [None])[0]
        scope['user'] = await _get_user(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """Equivalente a AuthMiddlewareStack pero validando JWT por query param."""
    return JWTAuthMiddleware(inner)
