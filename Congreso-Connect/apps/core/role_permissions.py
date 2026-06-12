WILDCARD = '*'

ROLE_PERMISSIONS = {
    # admin tiene todos los permisos (wildcard)
    'admin': {WILDCARD},
    # registrador (personal de puerta): solo control de aforo / asistencia
    'registrador': {'view:attendance', 'create:attendance'},
    # user sin permisos por defecto — agregar 'accion:recurso' segun se necesite
    'user': set(),
}


def has_permission(role, permission):
    perms = ROLE_PERMISSIONS.get(role, set())
    return WILDCARD in perms or permission in perms
