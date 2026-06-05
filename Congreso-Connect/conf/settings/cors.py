"""
Configuracion de CORS (Cross-Origin Resource Sharing).
"""

from decouple import Csv

from ._env import config

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:4200,http://127.0.0.1:4200,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080',
    cast=Csv(),
)

CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)

__all__ = [
    'CORS_ALLOWED_ORIGINS',
    'CORS_ALLOW_CREDENTIALS',
]
