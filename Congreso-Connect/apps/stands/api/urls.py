from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.stands.api.views import PublicStandTypeListView, StandTypeViewSet

router = DefaultRouter()
router.register('stand-types', StandTypeViewSet, basename='stand-types')

urlpatterns = [
    # Lectura publica para la landing (sin auth).
    path('public/stand-types/', PublicStandTypeListView.as_view(), name='public-stand-types'),
] + router.urls
