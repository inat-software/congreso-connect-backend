from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attendance.api.serializers import (
    AttendanceSerializer,
    ManualAttendanceSerializer,
    ScanSerializer,
)
from apps.attendance.models import Attendance
from apps.core.permissions import HasRolePermission

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary='Listar asistencias (aforo)', tags=['Asistencia']),
)
class AttendanceViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Control de aforo. El registrador (o admin) registra y lista quien esta
    fisicamente dentro del evento, por escaneo de QR o por ingreso manual.
    SEGURIDAD: requiere permiso `view/create:attendance` (registrador o admin).
    """
    serializer_class = AttendanceSerializer
    permission_classes = (IsAuthenticated, HasRolePermission)
    permission_resource = 'attendance'
    permission_action_map = {
        'scan': 'create:attendance',
        'manual': 'create:attendance',
    }
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'dni']
    ordering_fields = ['created_at', 'last_name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Attendance.objects.select_related('user').all()

    @extend_schema(
        summary='Registrar asistencia por QR',
        request=ScanSerializer,
        tags=['Asistencia'],
    )
    @action(detail=False, methods=['post'])
    def scan(self, request):
        ser = ScanSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data['token']

        user = User.objects.filter(qr_token=token).first()
        if not user:
            return Response(
                {'detail': 'Codigo QR no valido o no corresponde a ningun asistente.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        attendance, created = Attendance.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'method': Attendance.Method.QR,
                'registered_by': request.user,
            },
        )
        return Response(
            {
                'created': created,
                'attendance': AttendanceSerializer(attendance).data,
                'detail': (
                    'Asistencia registrada.' if created
                    else 'Esta persona ya estaba registrada.'
                ),
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(
        summary='Registrar asistencia manual',
        request=ManualAttendanceSerializer,
        tags=['Asistencia'],
    )
    @action(detail=False, methods=['post'])
    def manual(self, request):
        ser = ManualAttendanceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dni = ser.validated_data.get('dni', '').strip()

        existing = Attendance.objects.filter(dni=dni).first() if dni else None
        if existing:
            return Response(
                {
                    'created': False,
                    'attendance': AttendanceSerializer(existing).data,
                    'detail': 'Ya existe un registro con ese DNI.',
                },
                status=status.HTTP_200_OK,
            )

        attendance = ser.save(
            method=Attendance.Method.MANUAL,
            registered_by=request.user,
        )
        return Response(
            {
                'created': True,
                'attendance': AttendanceSerializer(attendance).data,
                'detail': 'Asistencia registrada.',
            },
            status=status.HTTP_201_CREATED,
        )
