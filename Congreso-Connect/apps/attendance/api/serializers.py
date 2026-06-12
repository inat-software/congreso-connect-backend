from rest_framework import serializers

from apps.attendance.models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    """Lectura de un registro de asistencia."""
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = (
            'id', 'first_name', 'last_name', 'full_name', 'dni',
            'method', 'method_display', 'created_at',
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()


class ManualAttendanceSerializer(serializers.ModelSerializer):
    """Ingreso manual: el registrador tipea nombres, apellidos y DNI."""

    class Meta:
        model = Attendance
        fields = ('first_name', 'last_name', 'dni')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'dni': {'required': True},
        }


class ScanSerializer(serializers.Serializer):
    """Recibe el token (UUID) que codifica el QR escaneado."""
    token = serializers.UUIDField()
