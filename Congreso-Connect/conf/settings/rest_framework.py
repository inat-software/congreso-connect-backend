"""
Configuracion de Django REST Framework, SimpleJWT y drf-spectacular (Swagger/OpenAPI).
"""

from datetime import timedelta

from ._env import config

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': config('PAGE_SIZE', default=20, cast=int),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# SimpleJWT Configuration
SIMPLE_JWT = {
    # Duracion de tokens
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_LIFETIME_MINUTES', default=30, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_LIFETIME_DAYS', default=7, cast=int)),

    # Rotacion de refresh tokens: cada vez que se refresca, se emite un nuevo refresh token
    'ROTATE_REFRESH_TOKENS': True,
    # Blacklist del refresh token anterior al rotar (evita reutilizacion)
    'BLACKLIST_AFTER_ROTATION': True,

    # Algoritmo y tipo de token
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # Claims del token
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',

    # Claims personalizados (se inyectan via serializer custom)
    'TOKEN_OBTAIN_SERIALIZER': 'apps.user.api.serializers.CustomTokenObtainPairSerializer',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Congreso Connect',
    'DESCRIPTION': 'API de Congreso Connect — autenticacion JWT y gestion de usuarios',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    # Soporte para JWT en Swagger UI
    'SECURITY': [{'BearerAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}

__all__ = [
    'REST_FRAMEWORK',
    'SIMPLE_JWT',
    'SPECTACULAR_SETTINGS',
]
