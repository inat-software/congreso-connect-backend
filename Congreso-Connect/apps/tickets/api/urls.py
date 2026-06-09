from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.tickets.api.views import PublicTicketTypeListView, TicketTypeViewSet

router = DefaultRouter()
router.register('ticket-types', TicketTypeViewSet, basename='ticket-types')

urlpatterns = [
    # Lectura publica para la landing (sin auth).
    path('public/ticket-types/', PublicTicketTypeListView.as_view(), name='public-ticket-types'),
] + router.urls
