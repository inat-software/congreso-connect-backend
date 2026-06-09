from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsAdminUser
from apps.stands.models import StandType
from apps.stands.api.serializers import (
    PublicStandTypeSerializer,
    StandTypeSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='Listar tipos de stand', tags=['Stands']),
    retrieve=extend_schema(summary='Detalle de tipo de stand', tags=['Stands']),
    create=extend_schema(summary='Crear tipo de stand', tags=['Stands']),
    update=extend_schema(summary='Editar tipo de stand', tags=['Stands']),
    partial_update=extend_schema(summary='Editar tipo de stand', tags=['Stands']),
    destroy=extend_schema(summary='Eliminar tipo de stand', tags=['Stands']),
)
class StandTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD de tipos de stand. SEGURIDAD: solo admin (maneja precios). La
    autorizacion se exige en el backend, no se confia en el frontend.
    """
    queryset = StandType.objects.all()
    serializer_class = StandTypeSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'dimensions']
    ordering_fields = ['sort_order', 'price', 'name', 'created_at']
    ordering = ['sort_order', 'id']


@extend_schema(
    summary='Tipos de stand activos (publico)',
    description='Lista los tipos de stand activos para la landing. Sin autenticacion.',
    tags=['Stands'],
)
class PublicStandTypeListView(generics.ListAPIView):
    """Lectura publica para la landing: solo tipos de stand activos."""
    serializer_class = PublicStandTypeSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return StandType.objects.filter(is_active=True).order_by('sort_order', 'id')
