from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.user.models import CustomUser, ExpositorProfile


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


@admin.register(ExpositorProfile)
class ExpositorProfileAdmin(admin.ModelAdmin):
    """Permite al administrador revisar y aprobar expositores pendientes."""

    list_display = ('razon_social', 'ruc', 'user', 'approval_status', 'created_at')
    list_filter = ('approval_status',)
    search_fields = ('razon_social', 'ruc', 'user__email')
    list_editable = ('approval_status',)
    ordering = ('-created_at',)
    autocomplete_fields = ('user',)
