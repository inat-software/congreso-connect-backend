from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.tickets.api.views import (
    AdminOrderViewSet,
    OrderViewSet,
    PublicTicketTypeListView,
    TicketTypeViewSet,
)

router = DefaultRouter()
router.register('ticket-types', TicketTypeViewSet, basename='ticket-types')
router.register('orders', OrderViewSet, basename='orders')
router.register('admin/orders', AdminOrderViewSet, basename='admin-orders')

urlpatterns = [
    # Lectura publica para la landing (sin auth).
    path('public/ticket-types/', PublicTicketTypeListView.as_view(), name='public-ticket-types'),
] + router.urls
