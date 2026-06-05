"""
ASGI config para el proyecto Congreso Connect.
Configura Django Channels para manejar HTTP y WebSocket.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

# Inicializar Django ANTES de importar routing (los consumers dependen de models)
django_asgi_app = get_asgi_application()

from conf.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    # HTTP — manejado por Django normalmente
    'http': django_asgi_app,
    # WebSocket — autenticacion + routing
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
