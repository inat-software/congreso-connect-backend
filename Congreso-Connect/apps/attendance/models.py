from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Attendance(TimeStampedModel):
    """
    Una persona registrada como presente fisicamente en el evento (control de
    aforo). Se crea al escanear el QR de un asistente (queda vinculada al
    usuario) o por ingreso manual del registrador (nombres/apellidos/DNI).
    """

    class Method(models.TextChoices):
        QR = 'qr', 'Escaneo de QR'
        MANUAL = 'manual', 'Ingreso manual'

    first_name = models.CharField('nombres', max_length=150)
    last_name = models.CharField('apellidos', max_length=150)
    dni = models.CharField('DNI', max_length=20, blank=True)
    method = models.CharField(
        'metodo', max_length=10, choices=Method.choices,
        default=Method.MANUAL, db_index=True,
    )
    # Si vino de escanear el QR de un asistente, queda vinculada a su usuario
    # (1 a 1: cada asistente entra una sola vez). En manual queda en null.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='attendance', verbose_name='usuario',
    )
    # Registrador (personal de puerta) que hizo el check-in.
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='registered_attendances',
        verbose_name='registrado por',
    )

    class Meta:
        app_label = 'attendance'
        db_table = 'attendance_attendance'
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.get_method_display()})'
