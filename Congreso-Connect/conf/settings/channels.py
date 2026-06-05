"""
Configuracion de Django Channels (WebSockets).
Usa Redis como channel layer si USE_REDIS=True, caso contrario InMemory.
InMemory solo es apto para desarrollo (un solo proceso).
"""

from ._env import config

USE_REDIS = config('USE_REDIS', default=False, cast=bool)

if USE_REDIS:
    REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/1')
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
                'capacity': 1500,
                'expiry': 10,
            },
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

__all__ = ['CHANNEL_LAYERS']
