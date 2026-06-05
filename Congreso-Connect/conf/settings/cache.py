"""
Configuracion de cache (Redis).
Cuando USE_REDIS=False, Django usa su cache en memoria por defecto.
"""

from ._env import config

USE_REDIS = config('USE_REDIS', default=False, cast=bool)

if USE_REDIS:
    REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/1')
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }

__all__ = ['CACHES'] if USE_REDIS else []
