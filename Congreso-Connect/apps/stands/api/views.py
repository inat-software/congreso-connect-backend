from django.utils import timezone
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsAdminUser, IsApprovedExpositor
from apps.stands.models import StandReservation, StandType
from apps.stands.api.serializers import (
    PublicStandTypeSerializer,
    StandReservationAdminSerializer,
    StandReservationCreateSerializer,
    StandReservationSerializer,
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


@extend_schema_view(
    list=extend_schema(summary='Mis reservas de stand', tags=['Reservas de stand']),
    retrieve=extend_schema(summary='Detalle de mi reserva', tags=['Reservas de stand']),
    create=extend_schema(summary='Reservar stand', tags=['Reservas de stand']),
)
class StandReservationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Reservas del expositor autenticado: reservar (solo expositor APROBADO) y
    listar/ver las propias. Cada quien solo ve SUS reservas.
    """

    def get_permissions(self):
        # Reservar exige expositor aprobado; el resto, solo autenticado.
        if self.action == 'create':
            return [IsApprovedExpositor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return StandReservation.objects.filter(user=self.request.user).select_related('stand_type')

    def get_serializer_class(self):
        return (
            StandReservationCreateSerializer
            if self.action == 'create'
            else StandReservationSerializer
        )

    def create(self, request, *args, **kwargs):
        serializer = StandReservationCreateSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()
        return Response(
            StandReservationSerializer(reservation).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(summary='Listar reservas (admin)', tags=['Reservas de stand']),
    retrieve=extend_schema(summary='Detalle de reserva (admin)', tags=['Reservas de stand']),
)
class AdminStandReservationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Gestion de reservas para el admin: listar (filtrable por estado), marcar
    pagada (simula la pasarela) y cancelar. Solo admin.
    """
    serializer_class = StandReservationAdminSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['stand_type_name', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = StandReservation.objects.select_related('user', 'stand_type').all()
        status_param = self.request.query_params.get('status')
        if status_param in StandReservation.Status.values:
            qs = qs.filter(status=status_param)
        return qs

    @extend_schema(summary='Marcar reserva como pagada', tags=['Reservas de stand'], request=None)
    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != StandReservation.Status.PAID:
            reservation.status = StandReservation.Status.PAID
            reservation.paid_at = timezone.now()
            reservation.save(update_fields=['status', 'paid_at', 'updated_at'])
        return Response(self.get_serializer(reservation).data)

    @extend_schema(summary='Cancelar reserva', tags=['Reservas de stand'], request=None)
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != StandReservation.Status.CANCELLED:
            reservation.status = StandReservation.Status.CANCELLED
            reservation.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(reservation).data)
