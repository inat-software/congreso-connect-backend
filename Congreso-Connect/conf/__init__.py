# Cargar Celery al iniciar Django para que autodiscover funcione
from .celery_app import app as celery_app

__all__ = ('celery_app',)
