from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.content.api.views import (
    B2BAgendaItemViewSet,
    B2BConfigAdminView,
    BannerViewSet,
    EventConfigAdminView,
    PublicB2BAgendaListView,
    PublicB2BConfigView,
    PublicBannerListView,
    PublicEventConfigView,
    PublicSpeakerListView,
    PublicSponsorListView,
    SpeakerViewSet,
    SponsorViewSet,
)

router = DefaultRouter()
router.register('speakers', SpeakerViewSet, basename='speakers')
router.register('sponsors', SponsorViewSet, basename='sponsors')
router.register('banners', BannerViewSet, basename='banners')
router.register('b2b-agenda', B2BAgendaItemViewSet, basename='b2b-agenda')

urlpatterns = [
    # Lectura publica para la landing (sin auth).
    path('public/speakers/', PublicSpeakerListView.as_view(), name='public-speakers'),
    path('public/sponsors/', PublicSponsorListView.as_view(), name='public-sponsors'),
    path('public/banners/', PublicBannerListView.as_view(), name='public-banners'),
    path('public/b2b-config/', PublicB2BConfigView.as_view(), name='public-b2b-config'),
    path('public/b2b-agenda/', PublicB2BAgendaListView.as_view(), name='public-b2b-agenda'),
    path('public/event-config/', PublicEventConfigView.as_view(), name='public-event-config'),
    # Configuración (singletons, admin).
    path('admin/event-config/', EventConfigAdminView.as_view(), name='admin-event-config'),
    path('admin/b2b-config/', B2BConfigAdminView.as_view(), name='admin-b2b-config'),
] + router.urls
