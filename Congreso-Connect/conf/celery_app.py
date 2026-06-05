"""
Instancia de Celery para el proyecto Congreso Connect.
Se importa en conf/__init__.py para que se cargue al iniciar Django.
"""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('congreso-connect')

# Leer configuracion desde settings con prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks en todas las apps registradas (busca tasks.py)
app.autodiscover_tasks()
