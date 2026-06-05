from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que provee campos de timestamp reutilizables.
    Todos los modelos del proyecto deben heredar de este.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
