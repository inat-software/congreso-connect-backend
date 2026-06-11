"""
Logica de negocio del chat, reutilizable tanto por la API REST como por el
consumer de WebSocket (Fase 3). Mantener aqui cualquier escritura para que
ambos caminos compartan exactamente las mismas reglas.
"""
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone

from apps.chat.models import Conversation, Message

# Anti-spam: como maximo RATE_LIMIT_MAX mensajes por RATE_LIMIT_WINDOW segundos
# por usuario (ventana fija). Generoso para una persona, frena bucles/abusos.
RATE_LIMIT_MAX = 20
RATE_LIMIT_WINDOW = 10


class ChatRateLimitError(Exception):
    """El usuario supero el limite de mensajes por ventana de tiempo."""


def _check_rate_limit(user):
    key = f'chat:rate:{user.pk}'
    try:
        count = cache.incr(key)
    except ValueError:
        # La clave no existe (o expiro): inicia una nueva ventana.
        cache.set(key, 1, RATE_LIMIT_WINDOW)
        count = 1
    if count > RATE_LIMIT_MAX:
        raise ChatRateLimitError()


def get_or_create_conversation(user_a, user_b):
    """
    Devuelve (creando si hace falta) la conversacion 1 a 1 entre dos usuarios.
    Normaliza el par (pk menor primero) para que exista una sola por pareja.
    """
    if user_a.pk == user_b.pk:
        raise ValueError('No se puede crear una conversacion con uno mismo.')
    low, high = (user_a, user_b) if user_a.pk < user_b.pk else (user_b, user_a)
    conversation, _created = Conversation.objects.get_or_create(
        user_a=low, user_b=high,
    )
    return conversation


def send_message(conversation, sender, body):
    """
    Persiste un mensaje y actualiza el `last_message_at` de la conversacion.

    Asume que el `body` ya viene validado/limpiado (lo hace el serializer o el
    consumer). Aplica rate-limit por remitente; lanza `ChatRateLimitError` si se
    supera. Devuelve el `Message` creado.
    """
    _check_rate_limit(sender)
    message = Message.objects.create(
        conversation=conversation, sender=sender, body=body,
    )
    conversation.last_message_at = message.created_at
    conversation.save(update_fields=['last_message_at', 'updated_at'])
    return message


def mark_conversation_read(conversation, reader):
    """
    Marca como leidos todos los mensajes ENTRANTES (no enviados por `reader`)
    que aun esten sin leer. Devuelve cuantos se actualizaron.
    """
    return (
        conversation.messages
        .filter(read_at__isnull=True)
        .exclude(sender=reader)
        .update(read_at=timezone.now())
    )


def user_conversations(user):
    """Conversaciones del usuario, anotadas con su numero de no leidos."""
    return (
        Conversation.objects
        .filter(Q(user_a=user) | Q(user_b=user))
        .select_related('user_a', 'user_b')
        .annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__read_at__isnull=True) & ~Q(messages__sender=user),
            ),
        )
        .order_by('-last_message_at', '-created_at')
    )


def last_messages_by_conversation(conversation_ids):
    """
    Devuelve un dict {conversation_id: ultimo Message} para los ids dados,
    en una sola consulta (evita N+1 al armar la bandeja y la lista de contactos).

    Usa DISTINCT ON (PostgreSQL, el motor por defecto del proyecto): toma el
    mensaje mas reciente por conversacion sin traer todo el historial.
    """
    if not conversation_ids:
        return {}
    qs = (
        Message.objects
        .filter(conversation_id__in=conversation_ids)
        .select_related('sender')
        .order_by('conversation_id', '-created_at')
        .distinct('conversation_id')
    )
    return {msg.conversation_id: msg for msg in qs}
