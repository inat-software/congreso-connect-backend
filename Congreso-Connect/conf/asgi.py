"""
ASGI config para el proyecto Congreso Connect.
Configura Django Channels para manejar HTTP y WebSocket.
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

# Inicializar Django ANTES de importar routing (los consumers dependen de models)
django_asgi_app = get_asgi_application()

from django.conf import settings  # noqa: E402

from apps.chat.ws_auth import JWTAuthMiddlewareStack  # noqa: E402
from conf.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    # HTTP — manejado por Django normalmente
    'http': django_asgi_app,
    # WebSocket — valida el Origin contra el MISMO allowlist que CORS (REST),
    # autentica por JWT (query param) y enruta a los consumers.
    'websocket': OriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
        settings.CORS_ALLOWED_ORIGINS,
    ),
})
