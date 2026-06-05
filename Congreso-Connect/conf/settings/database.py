"""
Configuracion de la base de datos.
Soporta MySQL, PostgreSQL y SQLite3 seleccionables mediante DATABASE_ENGINE.
"""

from ._env import config, BASE_DIR

DATABASE_ENGINE = config('DATABASE_ENGINE', default='postgresql')

_ENGINE_MAP = {
    'mysql': 'django.db.backends.mysql',
    'postgresql': 'django.db.backends.postgresql',
    'sqlite3': 'django.db.backends.sqlite3',
}

if DATABASE_ENGINE == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': _ENGINE_MAP['sqlite3'],
            'NAME': config('DATABASE_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': _ENGINE_MAP.get(DATABASE_ENGINE, _ENGINE_MAP['postgresql']),
            'NAME': config('DATABASE_NAME', default='congreso-connect'),
            'USER': config('DATABASE_USER'),
            'PASSWORD': config('DATABASE_PASSWORD'),
            'HOST': config('DATABASE_HOST', default='127.0.0.1'),
            'PORT': config(
                'DATABASE_PORT',
                default='5432' if DATABASE_ENGINE == 'postgresql' else '5432',
            ),
        }
    }

__all__ = ['DATABASES']
