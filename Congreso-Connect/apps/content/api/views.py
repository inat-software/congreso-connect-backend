from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsAdminUser
from apps.content.models import Banner, EventConfig, Speaker, Sponsor
from apps.content.api.serializers import (
    BannerSerializer,
    EventConfigSerializer,
    PublicBannerSerializer,
    PublicEventConfigSerializer,
    PublicSpeakerSerializer,
    PublicSponsorSerializer,
    SpeakerSerializer,
    SponsorSerializer,
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


@extend_schema_view(
    list=extend_schema(summary='Listar patrocinadores', tags=['Patrocinadores']),
    retrieve=extend_schema(summary='Detalle de patrocinador', tags=['Patrocinadores']),
    create=extend_schema(summary='Crear patrocinador', tags=['Patrocinadores']),
    update=extend_schema(summary='Editar patrocinador', tags=['Patrocinadores']),
    partial_update=extend_schema(summary='Editar patrocinador', tags=['Patrocinadores']),
    destroy=extend_schema(summary='Eliminar patrocinador', tags=['Patrocinadores']),
)
class SponsorViewSet(viewsets.ModelViewSet):
    """CRUD de patrocinadores. SEGURIDAD: solo admin. Acepta multipart (logo)."""
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'tier']
    ordering_fields = ['sort_order', 'name', 'created_at']
    ordering = ['sort_order', 'id']


@extend_schema(
    summary='Patrocinadores activos (publico)',
    description='Lista los patrocinadores activos para la landing. Sin autenticacion.',
    tags=['Patrocinadores'],
)
class PublicSponsorListView(generics.ListAPIView):
    """Lectura publica para la landing: solo patrocinadores activos."""
    serializer_class = PublicSponsorSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return Sponsor.objects.filter(is_active=True).order_by('sort_order', 'id')


@extend_schema_view(
    list=extend_schema(summary='Listar banners', tags=['Banners']),
    retrieve=extend_schema(summary='Detalle de banner', tags=['Banners']),
    create=extend_schema(summary='Crear banner', tags=['Banners']),
    update=extend_schema(summary='Editar banner', tags=['Banners']),
    partial_update=extend_schema(summary='Editar banner', tags=['Banners']),
    destroy=extend_schema(summary='Eliminar banner', tags=['Banners']),
)
class BannerViewSet(viewsets.ModelViewSet):
    """CRUD de banners del carrusel. SEGURIDAD: solo admin. Acepta multipart (imagen)."""
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'eyebrow', 'subtitle']
    ordering_fields = ['sort_order', 'title', 'created_at']
    ordering = ['sort_order', 'id']


@extend_schema(
    summary='Banners activos (publico)',
    description='Lista los banners activos del carrusel para la landing. Sin autenticacion.',
    tags=['Banners'],
)
class PublicBannerListView(generics.ListAPIView):
    """Lectura publica para la landing: solo banners activos."""
    serializer_class = PublicBannerSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return Banner.objects.filter(is_active=True).order_by('sort_order', 'id')


@extend_schema(summary='Configuración del evento (admin)', tags=['Configuración'])
class EventConfigAdminView(generics.RetrieveUpdateAPIView):
    """Lee y edita la configuración del evento (singleton). Solo admin."""
    serializer_class = EventConfigSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get_object(self):
        return EventConfig.load()


@extend_schema(summary='Configuración del evento (público)', tags=['Configuración'])
class PublicEventConfigView(generics.RetrieveAPIView):
    """Configuración del evento para la landing (sin auth)."""
    serializer_class = PublicEventConfigSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return EventConfig.load()
