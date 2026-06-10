from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.content.api.views import (
    EventConfigAdminView,
    PublicEventConfigView,
    PublicSpeakerListView,
    PublicSponsorListView,
    SpeakerViewSet,
    SponsorViewSet,
)

router = DefaultRouter()
router.register('speakers', SpeakerViewSet, basename='speakers')
router.register('sponsors', SponsorViewSet, basename='sponsors')

urlpatterns = [
    # Lectura publica para la landing (sin auth).
    path('public/speakers/', PublicSpeakerListView.as_view(), name='public-speakers'),
    path('public/sponsors/', PublicSponsorListView.as_view(), name='public-sponsors'),
    path('public/event-config/', PublicEventConfigView.as_view(), name='public-event-config'),
    # Configuración del evento (singleton, admin).
    path('admin/event-config/', EventConfigAdminView.as_view(), name='admin-event-config'),
] + router.urls
