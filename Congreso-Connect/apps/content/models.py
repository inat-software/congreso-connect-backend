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


class EventConfig(TimeStampedModel):
    """Single-row event configuration (seccion Sede & Fechas)."""

    location_headline = models.CharField('titulo de ubicacion', max_length=150, default='Trujillo, Perú')
    location_description = models.TextField(
        'descripcion', blank=True,
        default='Nueva sede premium 5★ · Costa del Sol Wyndham Trujillo. Un espacio '
                'ideal para reuniones estratégicas, networking y experiencias culturales.',
    )
    dates = models.CharField('fechas', max_length=150, blank=True, default='21, 22 y 23 de octubre 2026')
    venue = models.CharField('sede', max_length=200, blank=True, default='Costa del Sol Wyndham · Trujillo')
    guest_country = models.CharField('pais invitado', max_length=100, blank=True, default='Chile')
    previous_edition_label = models.CharField('etiqueta edicion anterior', max_length=100, blank=True, default='Edición 2025')
    previous_edition_stats = models.CharField(
        'stats edicion anterior', max_length=200, blank=True,
        default='+200 empresas · +380 reuniones B2B',
    )
    map_query = models.CharField('consulta del mapa', max_length=255, blank=True, default='Costa del Sol Wyndham Trujillo')

    class Meta:
        app_label = 'content'
        db_table = 'content_event_config'
        verbose_name = 'Configuración del evento'
        verbose_name_plural = 'Configuración del evento'

    def save(self, *args, **kwargs):
        self.pk = 1  # siempre la misma fila → singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Configuración del evento'


class Sponsor(TimeStampedModel):
    """A sponsor/partner shown in the landing."""

    name = models.CharField('nombre', max_length=150)
    logo = models.ImageField('logo', upload_to='sponsors/%Y/%m/')
    website = models.URLField('sitio web', blank=True)
    tier = models.CharField('nivel', max_length=50, blank=True)
    is_active = models.BooleanField('activo', default=True)
    sort_order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        app_label = 'content'
        db_table = 'content_sponsor'
        verbose_name = 'Patrocinador'
        verbose_name_plural = 'Patrocinadores'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Banner(TimeStampedModel):
    """
    Una diapositiva del carrusel principal del landing. El admin puede crear
    tantas como quiera; la imagen se guarda fisicamente en /media/banners/.
    """

    image = models.ImageField('imagen', upload_to='banners/%Y/%m/')
    eyebrow = models.CharField('etiqueta superior', max_length=150, blank=True)
    title = models.CharField('titulo', max_length=200, blank=True)
    subtitle = models.CharField('subtitulo', max_length=300, blank=True)
    is_active = models.BooleanField('activo', default=True)
    sort_order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        app_label = 'content'
        db_table = 'content_banner'
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title or f'Banner #{self.pk}'
