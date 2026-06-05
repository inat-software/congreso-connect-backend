"""
Configuracion base de Django: aplicaciones, middleware, templates, archivos estaticos.
"""

from ._env import BASE_DIR

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceros
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'corsheaders',
    'channels',
    # Apps propias
    'apps.core',
    'apps.user.apps.UserConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'
ASGI_APPLICATION = 'conf.asgi.application'

STATIC_URL = 'static/'

# Media files (avatares de usuario)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Limites de subida de archivos (avatares). Aumentar si se requieren archivos mayores.
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB — usado por validadores de serializers
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_BYTES
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # 2 MB — más allá de eso, streamear a disco
DATA_UPLOAD_MAX_NUMBER_FILES = 20

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'user.CustomUser'

__all__ = [
    'BASE_DIR',
    'INSTALLED_APPS',
    'MIDDLEWARE',
    'ROOT_URLCONF',
    'TEMPLATES',
    'WSGI_APPLICATION',
    'ASGI_APPLICATION',
    'STATIC_URL',
    'MEDIA_URL',
    'MEDIA_ROOT',
    'MAX_UPLOAD_SIZE_BYTES',
    'DATA_UPLOAD_MAX_MEMORY_SIZE',
    'FILE_UPLOAD_MAX_MEMORY_SIZE',
    'DATA_UPLOAD_MAX_NUMBER_FILES',
    'DEFAULT_AUTO_FIELD',
    'AUTH_USER_MODEL',
]
