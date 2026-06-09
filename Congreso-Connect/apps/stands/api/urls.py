from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.stands.api.views import (
    AdminStandReservationViewSet,
    PublicStandTypeListView,
    StandReservationViewSet,
    StandTypeViewSet,
)

router = DefaultRouter()
router.register('stand-types', StandTypeViewSet, basename='stand-types')
router.register('stand-reservations', StandReservationViewSet, basename='stand-reservations')
router.register('admin/stand-reservations', AdminStandReservationViewSet, basename='admin-stand-reservations')

urlpatterns = [
    # Lectura publica para la landing (sin auth).
    path('public/stand-types/', PublicStandTypeListView.as_view(), name='public-stand-types'),
] + router.urls
