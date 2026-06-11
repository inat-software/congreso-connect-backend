from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Conversation(TimeStampedModel):
    """
    Conversacion privada 1 a 1 entre dos usuarios.

    El par se guarda NORMALIZADO (user_a.pk < user_b.pk) para garantizar una
    unica conversacion por pareja sin importar quien la inicio. Usa siempre
    `apps.chat.services.get_or_create_conversation` para crearla — nunca
    instancies este modelo a mano sin ordenar el par.
    """

    user_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_a',
        verbose_name='usuario A',
    )
    user_b = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_b',
        verbose_name='usuario B',
    )
    # Se actualiza al enviar cada mensaje para ordenar la bandeja sin un JOIN.
    last_message_at = models.DateTimeField(
        'ultimo mensaje', null=True, blank=True, db_index=True,
    )

    class Meta:
        app_label = 'chat'
        db_table = 'chat_conversation'
        verbose_name = 'Conversacion'
        verbose_name_plural = 'Conversaciones'
        ordering = ['-last_message_at', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user_a', 'user_b'], name='uniq_conversation_pair',
            ),
            # Refuerza la normalizacion del par a nivel de base de datos.
            models.CheckConstraint(
                condition=models.Q(user_a__lt=models.F('user_b')),
                name='conversation_pair_ordered',
            ),
        ]

    def __str__(self):
        return f'Conversacion #{self.pk}: {self.user_a_id} ↔ {self.user_b_id}'

    def other_user(self, me):
        """Devuelve el otro participante respecto de `me`."""
        return self.user_b if self.user_a_id == me.pk else self.user_a

    def has_participant(self, user):
        return user.pk in (self.user_a_id, self.user_b_id)


class Message(TimeStampedModel):
    """Mensaje dentro de una conversacion 1 a 1."""

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='conversacion',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='remitente',
    )
    body = models.TextField('mensaje')
    # null = no leido. Se setea cuando el destinatario marca como leido.
    read_at = models.DateTimeField('leido el', null=True, blank=True)

    class Meta:
        app_label = 'chat'
        db_table = 'chat_message'
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['created_at']
        indexes = [
            models.Index(
                fields=['conversation', 'created_at'],
                name='chat_msg_conv_created_idx',
            ),
        ]

    def __str__(self):
        return f'Mensaje #{self.pk} de {self.sender_id} en conv {self.conversation_id}'
