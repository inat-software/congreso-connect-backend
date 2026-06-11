from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from apps.chat.access import can_chat_with, chat_eligible_users
from apps.chat.models import Conversation
from apps.chat.services import (
    ChatRateLimitError,
    get_or_create_conversation,
    last_messages_by_conversation,
    mark_conversation_read,
    send_message,
    user_conversations,
)
from apps.chat.api.serializers import (
    ContactSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)
from apps.core.pagination import LargePagination, StandardPagination


@extend_schema(
    summary='Contactos disponibles para chatear',
    description=(
        'Usuarios con los que el usuario autenticado puede chatear (subconjunto '
        'habilitado), enriquecidos con la conversacion existente, ultimo mensaje '
        'y no leidos. Filtrable por ?search=.'
    ),
    parameters=[OpenApiParameter('search', str, description='Filtra por nombre o email')],
    tags=['Chat'],
)
class ContactListView(generics.ListAPIView):
    """Lista de usuarios habilitados para chatear (ver apps.chat.access)."""
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = chat_eligible_users(self.request.user)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )
        return qs.order_by('first_name', 'last_name', 'email')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['contact_meta'] = self._build_contact_meta()
        return ctx

    def _build_contact_meta(self):
        """
        Mapea {other_user_id: {conversation_id, last_message, unread_count}}
        para las conversaciones existentes del usuario. Acotado por la cantidad
        de conversaciones que tiene (no por el total de contactos).
        """
        me = self.request.user
        convs = list(user_conversations(me))
        last_map = last_messages_by_conversation([c.id for c in convs])
        meta = {}
        for conv in convs:
            other = conv.other_user(me)
            meta[other.pk] = {
                'conversation_id': conv.id,
                'last_message': last_map.get(conv.id),
                'unread_count': getattr(conv, 'unread_count', 0),
            }
        return meta


@extend_schema_view(
    list=extend_schema(summary='Mi bandeja de conversaciones', tags=['Chat']),
    retrieve=extend_schema(summary='Detalle de una conversacion', tags=['Chat']),
)
class ConversationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Conversaciones del usuario autenticado. SEGURIDAD: el queryset solo incluye
    conversaciones donde el usuario participa, asi cualquier id ajeno da 404.
    """
    serializer_class = ConversationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return user_conversations(self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        # Para list/retrieve precargamos los ultimos mensajes y evitamos N+1.
        # Acotado por la cantidad de conversaciones del usuario.
        if self.action in ('list', 'retrieve'):
            ids = list(self.get_queryset().values_list('id', flat=True))
            ctx['last_messages'] = last_messages_by_conversation(ids)
        return ctx

    @extend_schema(
        summary='Historial de mensajes / enviar mensaje',
        request=MessageCreateSerializer,
        responses=MessageSerializer,
        tags=['Chat'],
    )
    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        conversation = self.get_object()

        if request.method == 'POST':
            serializer = MessageCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                message = send_message(
                    conversation, request.user, serializer.validated_data['body'],
                )
            except ChatRateLimitError:
                return Response(
                    {'detail': 'Estas enviando mensajes muy rapido. Espera un momento.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            return Response(
                MessageSerializer(message, context={'request': request}).data,
                status=status.HTTP_201_CREATED,
            )

        # GET: historial paginado, mas RECIENTES primero (page 1 = ultimos
        # mensajes). El cliente invierte cada pagina para mostrarlos en orden y
        # pide la siguiente pagina para "cargar mas antiguos".
        qs = conversation.messages.select_related('sender').order_by('-created_at')
        paginator = LargePagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = MessageSerializer(page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)

    @extend_schema(summary='Marcar conversacion como leida', request=None, tags=['Chat'])
    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        conversation = self.get_object()
        marked = mark_conversation_read(conversation, request.user)
        return Response({'marked_read': marked})


@extend_schema(
    summary='Abrir/obtener conversacion con un usuario',
    description='Crea (o devuelve) la conversacion 1 a 1 con el usuario indicado.',
    request=None,
    responses=ConversationSerializer,
    tags=['Chat'],
)
class OpenConversationView(APIView):
    """POST /chat/conversations/with/<user_id>/ — abre el chat con alguien."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        me = request.user
        other = get_object_or_404(chat_eligible_users(me), pk=user_id)
        if not can_chat_with(me, other):
            return Response(
                {'detail': 'No puedes chatear con este usuario.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        conversation = get_or_create_conversation(me, other)
        # Re-leer con la anotacion de no leidos para una respuesta consistente.
        conversation = user_conversations(me).get(pk=conversation.pk)
        ctx = {
            'request': request,
            'last_messages': last_messages_by_conversation([conversation.pk]),
        }
        return Response(ConversationSerializer(conversation, context=ctx).data)
