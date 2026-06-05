from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.user.managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado.
    Usa email como identificador principal y define los roles del sistema.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
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
