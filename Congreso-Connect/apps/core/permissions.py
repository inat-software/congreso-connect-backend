from rest_framework.permissions import BasePermission

from apps.core.role_permissions import has_permission


class IsAdminUser(BasePermission):
    """Solo permite acceso a usuarios con rol admin."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsAuthenticatedOrCreateOnly(BasePermission):
    """
    Permite crear sin autenticacion, lectura requiere autenticacion.
    Util para endpoints como respuestas de encuestas.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_authenticated


class HasRolePermission(BasePermission):
    """
    Permiso generico basado en accion:recurso.
    El ViewSet debe definir `permission_resource = 'nombre'`.
    Mapea la accion DRF (list, create, destroy...) al permiso correspondiente.
    Acciones custom se mapean via `permission_action_map` en el ViewSet.
    """

    ACTION_MAP = {
        'list': 'view',
        'retrieve': 'view',
        'create': 'create',
        'update': 'edit',
        'partial_update': 'edit',
        'destroy': 'delete',
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        resource = getattr(view, 'permission_resource', None)
        if not resource:
            return False

        action = getattr(view, 'action', None)
        custom_map = getattr(view, 'permission_action_map', {})

        if action in custom_map:
            perm = custom_map[action]
        elif action in self.ACTION_MAP:
            perm = f'{self.ACTION_MAP[action]}:{resource}'
        else:
            perm = f'view:{resource}'

        return has_permission(request.user.role, perm)
