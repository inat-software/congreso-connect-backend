from django.utils import timezone
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsAdminUser
from apps.tickets.models import Order, TicketType
from apps.tickets.api.serializers import (
    OrderAdminSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    PublicTicketTypeSerializer,
    TicketTypeSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='Listar tipos de entrada', tags=['Entradas']),
    retrieve=extend_schema(summary='Detalle de tipo de entrada', tags=['Entradas']),
    create=extend_schema(summary='Crear tipo de entrada', tags=['Entradas']),
    update=extend_schema(summary='Editar tipo de entrada', tags=['Entradas']),
    partial_update=extend_schema(summary='Editar tipo de entrada', tags=['Entradas']),
    destroy=extend_schema(summary='Eliminar tipo de entrada', tags=['Entradas']),
)
class TicketTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD de tipos de entrada. SEGURIDAD: solo admin (maneja precios). La
    autorizacion se exige en el backend, no se confia en el frontend.
    """
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'price', 'name', 'created_at']
    ordering = ['sort_order', 'id']


@extend_schema(
    summary='Tipos de entrada activos (publico)',
    description='Lista los tipos de entrada activos para la landing. Sin autenticacion.',
    tags=['Entradas'],
)
class PublicTicketTypeListView(generics.ListAPIView):
    """Lectura publica para la landing: solo tipos de entrada activos."""
    serializer_class = PublicTicketTypeSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return TicketType.objects.filter(is_active=True).order_by('sort_order', 'id')


@extend_schema_view(
    list=extend_schema(summary='Mis órdenes', tags=['Órdenes']),
    retrieve=extend_schema(summary='Detalle de mi orden', tags=['Órdenes']),
    create=extend_schema(summary='Comprar entrada', tags=['Órdenes']),
)
class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Órdenes del usuario autenticado: comprar (crea una orden pendiente) y
    listar/ver las propias. Cada quien solo ve SUS órdenes.
    """
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('ticket_type')

    def get_serializer_class(self):
        return OrderCreateSerializer if self.action == 'create' else OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        # Devolver la orden completa (no solo el input).
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(summary='Listar órdenes (admin)', tags=['Órdenes']),
    retrieve=extend_schema(summary='Detalle de orden (admin)', tags=['Órdenes']),
)
class AdminOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Gestión de órdenes para el admin: listar (filtrable por estado), marcar
    como pagada (simula la pasarela por ahora) y cancelar. Solo admin.
    """
    serializer_class = OrderAdminSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['ticket_type_name', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Order.objects.select_related('user', 'ticket_type').all()
        status_param = self.request.query_params.get('status')
        if status_param in Order.Status.values:
            qs = qs.filter(status=status_param)
        return qs

    @extend_schema(summary='Marcar orden como pagada', tags=['Órdenes'], request=None)
    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.Status.PAID:
            order.status = Order.Status.PAID
            order.paid_at = timezone.now()
            order.save(update_fields=['status', 'paid_at', 'updated_at'])
        return Response(self.get_serializer(order).data)

    @extend_schema(summary='Cancelar orden', tags=['Órdenes'], request=None)
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.Status.CANCELLED:
            order.status = Order.Status.CANCELLED
            order.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(order).data)
