"""
Configuracion de seguridad: clave secreta, modo debug, hosts permitidos,
validadores de contrasena.
"""

from decouple import Csv

from ._env import config

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Confiar en el header X-Forwarded-Proto del proxy reverso para detectar HTTPS.
# Esto permite que Django genere URLs absolutas con https:// cuando el proxy
# termina SSL y reenvia las peticiones por HTTP internamente.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Permitir iframes del mismo origen (los archivos media se eximen individualmente en urls.py)
X_FRAME_OPTIONS = 'SAMEORIGIN'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

__all__ = [
    'SECRET_KEY',
    'DEBUG',
    'ALLOWED_HOSTS',
    'SECURE_PROXY_SSL_HEADER',
    'X_FRAME_OPTIONS',
    'AUTH_PASSWORD_VALIDATORS',
]
