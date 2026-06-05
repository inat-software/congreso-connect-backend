from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.user.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Configuracion del admin de Django para CustomUser."""

    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # Campos del formulario de edicion
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informacion personal', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Rol y permisos', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

    # Campos del formulario de creacion
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
