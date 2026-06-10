from django.db import models

from apps.core.models import TimeStampedModel


class Speaker(TimeStampedModel):
    """A speaker/panelist at the international forum."""

    name = models.CharField('nombre', max_length=150)
    role = models.CharField('rol', max_length=150, blank=True)
    position = models.CharField('cargo', max_length=255, blank=True)
    bio = models.TextField('biografia', blank=True)
    topic = models.CharField('tema en el foro', max_length=255, blank=True)
    photo = models.ImageField('foto', upload_to='speakers/%Y/%m/', null=True, blank=True)
    is_active = models.BooleanField('activo', default=True)
    sort_order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        app_label = 'content'
        db_table = 'content_speaker'
        verbose_name = 'Disertante'
        verbose_name_plural = 'Disertantes'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name
