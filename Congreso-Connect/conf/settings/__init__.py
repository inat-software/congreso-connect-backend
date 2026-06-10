"""
Paquete de configuracion de Django para el proyecto Congreso Connect.
Importa todas las settings desde los sub-modulos.

DJANGO_SETTINGS_MODULE = 'conf.settings' resuelve a este __init__.py.
"""

from .base import *              # noqa: F401,F403
from .security import *          # noqa: F401,F403
from .database import *          # noqa: F401,F403
from .cors import *              # noqa: F401,F403
from .rest_framework import *    # noqa: F401,F403
from .cache import *             # noqa: F401,F403
from .channels import *          # noqa: F401,F403
from .celery import *            # noqa: F401,F403
from .i18n import *              # noqa: F401,F403
from .email import *             # noqa: F401,F403
