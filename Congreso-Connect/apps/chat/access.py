"""
Control de quien puede usar el chat (el "subconjunto de usuarios habilitados").

>>> PUNTO UNICO DE FILTRADO <<<
Hoy el chat esta abierto a TODOS los usuarios activos. Cuando se necesite
restringir quien puede chatear (por rol, por un flag `can_chat`, por estar
inscrito a un evento, etc.) se edita SOLO `chat_eligible_users` y el resto del
sistema (contactos, apertura de conversaciones, WebSocket) lo respeta
automaticamente.

Ejemplos de restriccion futura (descomentar/ajustar uno):
    # Solo expositores aprobados y admins:
    return qs.filter(Q(role='admin') | Q(role='expositor'))
    # Solo usuarios con un flag explicito en el modelo:
    return qs.filter(can_chat=True)
"""
from django.contrib.auth import get_user_model

User = get_user_model()


def chat_eligible_users(viewer):
    """
    Devuelve el queryset de usuarios con los que `viewer` puede chatear.

    HOY: todos los usuarios activos excepto uno mismo.
    Para restringir el chat a un subconjunto, edita SOLO esta funcion.
    """
    return User.objects.filter(is_active=True).exclude(pk=viewer.pk)


def can_chat_with(viewer, other):
    """True si `viewer` esta autorizado a iniciar/continuar chat con `other`."""
    if viewer.pk == other.pk:
        return False
    return chat_eligible_users(viewer).filter(pk=other.pk).exists()
