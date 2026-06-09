"""
URL configuration for Congreso Connect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.static import serve as static_serve
from django.views.decorators.clickjacking import xframe_options_exempt
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def api_root(request):
    """
    Vista raíz que muestra información de la API
    """
    return JsonResponse({
        'message': 'Bienvenido a la API de Congreso Connect',
        'version': '1.0.0',
        'endpoints': {
            'documentation': {
                'swagger': '/api/schema/swagger-ui/',
                'redoc': '/api/schema/redoc/',
                'openapi_schema': '/api/schema/',
            },
            'auth': '/api/v1/auth/',
            'users': '/api/v1/users/',
            'admin': '/admin/',
        }
    })


urlpatterns = [
    # Ruta raíz
    path('', api_root, name='api-root'),

    # Admin
    path('admin/', admin.site.urls),

    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Endpoints — Autenticacion
    path('api/v1/auth/', include('apps.user.api.urls')),

    # API Endpoints — Usuarios (CRUD admin)
    path('api/v1/users/', include('apps.user.api.user_urls')),

    # API Endpoints — Expositores (gestion admin: aprobar/rechazar)
    path('api/v1/expositores/', include('apps.user.api.expositor_urls')),

    # API Endpoints — Entradas (CRUD admin + lista publica para la landing)
    path('api/v1/', include('apps.tickets.api.urls')),

    # API Endpoints — Stands (CRUD admin + lista publica para la landing)
    path('api/v1/', include('apps.stands.api.urls')),
]

# Servir archivos media (avatares). Se registra siempre (no solo en DEBUG) porque
# en produccion (Coolify/Docker) Django tambien sirve los archivos media via Daphne.
@xframe_options_exempt
def serve_media(request, path, document_root=None):
    """Sirve archivos media sin restricción de X-Frame-Options."""
    response = static_serve(request, path, document_root=document_root)
    response['Access-Control-Allow-Origin'] = '*'
    return response


urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        serve_media,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
