from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsAdminUser
from apps.tickets.models import TicketType
from apps.tickets.api.serializers import (
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
