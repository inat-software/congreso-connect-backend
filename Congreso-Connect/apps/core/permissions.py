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


class IsApprovedExpositor(BasePermission):
    """
    Solo expositores con perfil APROBADO. Mensajes especificos segun el caso
    (no logueado / no es expositor / pendiente de aprobacion).
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            self.message = 'Debes iniciar sesion.'
            return False
        if user.role != 'expositor':
            self.message = 'Necesitas una cuenta de expositor para reservar.'
            return False
        profile = getattr(user, 'expositor_profile', None)
        # 'approved' = ExpositorProfile.ApprovalStatus.APPROVED
        if not profile or profile.approval_status != 'approved':
            self.message = 'Tu cuenta de expositor esta pendiente de aprobacion.'
            return False
        return True


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
