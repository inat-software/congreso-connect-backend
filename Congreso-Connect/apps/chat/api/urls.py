from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.chat.api.views import (
    ContactListView,
    ConversationViewSet,
    OpenConversationView,
)

router = DefaultRouter()
router.register('conversations', ConversationViewSet, basename='chat-conversations')

urlpatterns = [
    # Las rutas explicitas van ANTES del router para que 'with' no se
    # interprete como un <pk> de conversacion.
    path('contacts/', ContactListView.as_view(), name='chat-contacts'),
    path(
        'conversations/with/<int:user_id>/',
        OpenConversationView.as_view(),
        name='chat-open-conversation',
    ),
] + router.urls
