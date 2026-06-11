"""
Routing principal de WebSockets para Django Channels.
Aqui se registran las rutas ws:// del proyecto.
"""
from django.urls import path

from apps.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    # Chat 1 a 1. Auth por JWT en query param: ws/chat/?token=<access>
    path('ws/chat/', ChatConsumer.as_asgi()),
]
