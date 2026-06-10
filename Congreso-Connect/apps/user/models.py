from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel
from apps.user.managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado.
    Usa email como identificador principal y define los roles del sistema.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        EXPOSITOR = 'expositor', 'Expositor'
        USER = 'user', 'Usuario'

    # Eliminamos username como campo unico, usamos email
    username = None
    email = models.EmailField('email', unique=True)
    role = models.CharField(
        'rol',
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )
    phone = models.CharField('telefono', max_length=30, blank=True)
    avatar = models.ImageField(
        'foto de perfil',
        upload_to='users/avatars/%Y/%m/',
        blank=True,
        null=True,
    )
    # Token que codifica el QR del asistente (se genera cuando se necesita).
    # nullable+unique para poder migrar sin chocar con filas existentes.
    qr_token = models.UUIDField('token QR', null=True, blank=True, unique=True, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        app_label = 'user'
        db_table = 'user_customuser'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'

    @property
    def full_name(self):
        """Retorna nombre completo o email como fallback."""
        name = self.get_full_name().strip()
        return name if name else self.email


class ExpositorProfile(TimeStampedModel):
    """
    Perfil de empresa expositora, ligado 1:1 a un CustomUser con rol 'expositor'.
    Mantiene los datos de empresa y el estado de aprobacion fuera del modelo de
    usuario: un asistente comun NO tiene perfil; un expositor nace 'pendiente'
    hasta que un administrador lo aprueba.
    """

    class ApprovalStatus(models.TextChoices):
        PENDING = 'pending', 'Pendiente de aprobacion'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='expositor_profile',
        verbose_name='usuario',
    )
    razon_social = models.CharField('razon social', max_length=255)
    ruc = models.CharField('RUC / documento', max_length=20)
    approval_status = models.CharField(
        'estado de aprobacion',
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
        db_index=True,
    )

    class Meta:
        app_label = 'user'
        db_table = 'user_expositor_profile'
        verbose_name = 'Perfil de expositor'
        verbose_name_plural = 'Perfiles de expositor'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.razon_social} ({self.get_approval_status_display()})'
