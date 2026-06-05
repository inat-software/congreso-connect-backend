"""
Configuracion de Celery (tareas asincronas).
Usa Redis como broker si USE_REDIS=True, caso contrario usa el backend de memoria de Django.
"""

from ._env import config

USE_REDIS = config('USE_REDIS', default=False, cast=bool)

if USE_REDIS:
    REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/1')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
else:
    # Broker en memoria — solo para desarrollo (tareas se ejecutan sincrónicamente)
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# Configuracion comun
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = config('TIME_ZONE', default='UTC')

__all__ = [
    'CELERY_BROKER_URL',
    'CELERY_RESULT_BACKEND',
    'CELERY_ACCEPT_CONTENT',
    'CELERY_TASK_SERIALIZER',
    'CELERY_RESULT_SERIALIZER',
    'CELERY_TIMEZONE',
]
