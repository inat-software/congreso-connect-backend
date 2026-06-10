from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.content.api.views import PublicSpeakerListView, SpeakerViewSet

router = DefaultRouter()
router.register('speakers', SpeakerViewSet, basename='speakers')

urlpatterns = [
    # Lectura publica para la landing (sin auth).
    path('public/speakers/', PublicSpeakerListView.as_view(), name='public-speakers'),
] + router.urls
