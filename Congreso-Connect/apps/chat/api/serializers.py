from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.chat.models import Conversation, Message

User = get_user_model()


class ChatUserSerializer(serializers.ModelSerializer):
    """Datos minimos de un usuario para mostrarlo en el chat."""
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'avatar',
        )
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """Lectura de un mensaje. `is_mine` lo calcula respecto del usuario actual."""
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'id', 'conversation', 'sender', 'body', 'is_mine',
            'read_at', 'created_at',
        )
        read_only_fields = fields

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return bool(request and obj.sender_id == request.user.pk)


class MessageCreateSerializer(serializers.Serializer):
    """Valida el cuerpo de un mensaje entrante (REST o, mas adelante, WS)."""
    body = serializers.CharField(
        max_length=4000, trim_whitespace=True, allow_blank=False,
    )


class ConversationSerializer(serializers.ModelSerializer):
    """
    Conversacion para la bandeja: el otro participante, ultimo mensaje y
    cantidad de no leidos. Espera en el contexto:
      - `request`
      - `last_messages`: dict {conversation_id: Message} (opcional, evita N+1)
    """
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            'id', 'other_user', 'last_message', 'unread_count',
            'last_message_at', 'created_at',
        )
        read_only_fields = fields

    def get_other_user(self, obj):
        me = self.context['request'].user
        return ChatUserSerializer(obj.other_user(me), context=self.context).data

    def get_last_message(self, obj):
        last_map = self.context.get('last_messages')
        msg = last_map.get(obj.id) if last_map is not None else obj.messages.last()
        return MessageSerializer(msg, context=self.context).data if msg else None

    def get_unread_count(self, obj):
        # `unread_count` viene anotado desde services.user_conversations.
        return getattr(obj, 'unread_count', 0)


class ContactSerializer(ChatUserSerializer):
    """
    Un usuario con el que se puede chatear, enriquecido con el estado de la
    conversacion existente (si la hay). Espera en el contexto un dict
    `contact_meta`: {user_id: {conversation_id, last_message, unread_count}}.
    """
    conversation_id = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta(ChatUserSerializer.Meta):
        fields = ChatUserSerializer.Meta.fields + (
            'conversation_id', 'last_message', 'unread_count',
        )
        read_only_fields = fields

    def _meta_for(self, obj):
        return self.context.get('contact_meta', {}).get(obj.id)

    def get_conversation_id(self, obj):
        entry = self._meta_for(obj)
        return entry['conversation_id'] if entry else None

    def get_last_message(self, obj):
        entry = self._meta_for(obj)
        msg = entry['last_message'] if entry else None
        return MessageSerializer(msg, context=self.context).data if msg else None

    def get_unread_count(self, obj):
        entry = self._meta_for(obj)
        return entry['unread_count'] if entry else 0
