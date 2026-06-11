"""
WebSocket del chat (Django Channels).

Un usuario autenticado abre `ws/chat/?token=<access>` y queda suscrito a su
grupo personal `chat_user_<id>`. Los mensajes, indicadores de "escribiendo" y
recibos de lectura se entregan en vivo reenviando al grupo del OTRO participante
(y al propio, para sincronizar varias pestañas).

Toda la escritura en base de datos pasa por `apps.chat.services`, las mismas
reglas que usa la API REST.
"""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model

from apps.chat import services
from apps.chat.access import can_chat_with
from apps.chat.models import Conversation

User = get_user_model()

MAX_BODY = 4000


def user_group(user_id):
    return f'chat_user_{user_id}'


def serialize_message(message):
    """
    Forma plana de un mensaje para enviar por el socket. Coincide con los campos
    de `MessageSerializer` (REST) menos `is_mine`, que el cliente deduce
    comparando `sender` con su propio id.
    """
    return {
        'id': message.id,
        'conversation': message.conversation_id,
        'sender': message.sender_id,
        'body': message.body,
        'read_at': message.read_at.isoformat() if message.read_at else None,
        'created_at': message.created_at.isoformat(),
    }


class ChatConsumer(AsyncJsonWebsocketConsumer):
    # ---- ciclo de vida -----------------------------------------------------
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)  # 4401 = no autenticado (convencion app)
            return
        self.user = user
        self.group_name = user_group(user.pk)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # ---- mensajes entrantes del cliente ------------------------------------
    async def receive_json(self, content, **kwargs):
        handlers = {
            'message.send': self.handle_send,
            'typing': self.handle_typing,
            'read': self.handle_read,
        }
        handler = handlers.get(content.get('type'))
        if handler is None:
            await self.send_json({'type': 'error', 'detail': 'Tipo de evento desconocido.'})
            return
        await handler(content)

    async def handle_send(self, content):
        to_id = content.get('to')
        body = (content.get('body') or '').strip()[:MAX_BODY]
        if not to_id or not body:
            await self.send_json({'type': 'error', 'detail': 'Faltan datos del mensaje.'})
            return

        try:
            result = await self._persist_message(to_id, body)
        except services.ChatRateLimitError:
            await self.send_json(
                {'type': 'error', 'detail': 'Estás enviando mensajes muy rápido. Espera un momento.'}
            )
            return
        if result is None:
            await self.send_json(
                {'type': 'error', 'detail': 'No puedes enviar mensajes a este usuario.'}
            )
            return

        conversation_id, message, other_id = result
        event = {
            'type': 'chat.message',
            'conversation_id': conversation_id,
            'message': serialize_message(message),
        }
        # Al destinatario y a uno mismo (multi-pestaña / confirmacion de envio).
        await self.channel_layer.group_send(user_group(other_id), event)
        await self.channel_layer.group_send(self.group_name, event)

    async def handle_typing(self, content):
        conversation_id = content.get('conversation')
        state = bool(content.get('state'))
        other_id = await self._other_participant(conversation_id)
        if other_id is None:
            return
        await self.channel_layer.group_send(
            user_group(other_id),
            {
                'type': 'chat.typing',
                'conversation_id': conversation_id,
                'user_id': self.user.pk,
                'state': state,
            },
        )

    async def handle_read(self, content):
        conversation_id = content.get('conversation')
        result = await self._mark_read(conversation_id)
        if result is None:
            return
        other_id, _count = result
        await self.channel_layer.group_send(
            user_group(other_id),
            {
                'type': 'chat.read',
                'conversation_id': conversation_id,
                'reader_id': self.user.pk,
            },
        )

    # ---- eventos del grupo → cliente ---------------------------------------
    async def chat_message(self, event):
        await self.send_json({
            'type': 'message',
            'conversation_id': event['conversation_id'],
            'message': event['message'],
        })

    async def chat_typing(self, event):
        await self.send_json({
            'type': 'typing',
            'conversation_id': event['conversation_id'],
            'user_id': event['user_id'],
            'state': event['state'],
        })

    async def chat_read(self, event):
        await self.send_json({
            'type': 'read',
            'conversation_id': event['conversation_id'],
            'reader_id': event['reader_id'],
        })

    # ---- acceso a base de datos (sincrono → async) -------------------------
    @database_sync_to_async
    def _persist_message(self, to_id, body):
        try:
            other = User.objects.get(pk=to_id, is_active=True)
        except User.DoesNotExist:
            return None
        if not can_chat_with(self.user, other):
            return None
        conversation = services.get_or_create_conversation(self.user, other)
        message = services.send_message(conversation, self.user, body)
        return conversation.id, message, other.pk

    @database_sync_to_async
    def _other_participant(self, conversation_id):
        conv = self._participant_conversation(conversation_id)
        return conv.other_user(self.user).pk if conv else None

    @database_sync_to_async
    def _mark_read(self, conversation_id):
        conv = self._participant_conversation(conversation_id)
        if conv is None:
            return None
        count = services.mark_conversation_read(conv, self.user)
        return conv.other_user(self.user).pk, count

    def _participant_conversation(self, conversation_id):
        """Conversacion solo si el usuario participa en ella (si no, None)."""
        if not conversation_id:
            return None
        try:
            conv = Conversation.objects.select_related('user_a', 'user_b').get(
                pk=conversation_id,
            )
        except Conversation.DoesNotExist:
            return None
        return conv if conv.has_participant(self.user) else None
