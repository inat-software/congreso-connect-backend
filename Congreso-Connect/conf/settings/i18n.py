"""
Configuracion de internacionalizacion y zona horaria.
"""

from ._env import config

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_TZ = True

__all__ = [
    'LANGUAGE_CODE',
    'TIME_ZONE',
    'USE_I18N',
    'USE_TZ',
]
