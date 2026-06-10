from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsAdminUser
from apps.content.models import Speaker
from apps.content.api.serializers import (
    PublicSpeakerSerializer,
    SpeakerSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='Listar disertantes', tags=['Disertantes']),
    retrieve=extend_schema(summary='Detalle de disertante', tags=['Disertantes']),
    create=extend_schema(summary='Crear disertante', tags=['Disertantes']),
    update=extend_schema(summary='Editar disertante', tags=['Disertantes']),
    partial_update=extend_schema(summary='Editar disertante', tags=['Disertantes']),
    destroy=extend_schema(summary='Eliminar disertante', tags=['Disertantes']),
)
class SpeakerViewSet(viewsets.ModelViewSet):
    """
    CRUD de disertantes. SEGURIDAD: solo admin. Acepta multipart para la foto.
    """
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'role', 'position', 'topic']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'id']


@extend_schema(
    summary='Disertantes activos (publico)',
    description='Lista los disertantes activos para la landing. Sin autenticacion.',
    tags=['Disertantes'],
)
class PublicSpeakerListView(generics.ListAPIView):
    """Lectura publica para la landing: solo disertantes activos."""
    serializer_class = PublicSpeakerSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return Speaker.objects.filter(is_active=True).order_by('sort_order', 'id')
