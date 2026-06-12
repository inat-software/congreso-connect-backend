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

    # Datos de contacto que muestra el footer.
    contact_whatsapp_primary = models.CharField('whatsapp 1', max_length=40, blank=True, default='+51 931 388 602')
    contact_whatsapp_secondary = models.CharField('whatsapp 2', max_length=40, blank=True, default='+51 993 289 550')
    contact_email = models.EmailField('email de contacto', blank=True, default='camaradeturismolalibertad@gmail.com')
    contact_address = models.CharField(
        'direccion', max_length=255, blank=True,
        default='Jr. Independencia 467 · Plaza de Armas (2do piso), Trujillo',
    )

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
    """
    A sponsor/partner shown in the landing. Es un muro de logos: cada
    patrocinador es solo su avatar (logo) y un orden de aparicion.
    """

    name = models.CharField('nombre', max_length=150)
    logo = models.ImageField('logo (archivo)', upload_to='sponsors/%Y/%m/', null=True, blank=True)
    is_active = models.BooleanField('activo', default=True)
    sort_order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        app_label = 'content'
        db_table = 'content_sponsor'
        verbose_name = 'Patrocinador'
        verbose_name_plural = 'Patrocinadores'
        ordering = ['sort_order', 'id']

    def logo_display(self, request=None):
        """URL absoluta del logo subido (o None si aun no tiene)."""
        if self.logo:
            return request.build_absolute_uri(self.logo.url) if request else self.logo.url
        return None

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


class B2BConfig(TimeStampedModel):
    """
    Configuracion (singleton) de la seccion Rueda de Negocios B2B: textos y la
    tarjeta de inscripcion. La agenda se maneja aparte en B2BAgendaItem.
    """

    eyebrow = models.CharField('etiqueta', max_length=50, blank=True, default='B2B')
    title = models.CharField('titulo', max_length=150, blank=True, default='Rueda de Negocios')
    description = models.TextField(
        'descripcion', blank=True,
        default='Mesas exclusivas para reuniones estratégicas y alianzas comerciales '
                'con compradores nacionales e internacionales.',
    )
    card_title = models.CharField('titulo de la tarjeta', max_length=120, blank=True, default='Inscripción B2B')
    price_label = models.CharField('etiqueta de precio', max_length=120, blank=True, default='Precio regular')
    price = models.CharField('precio', max_length=60, blank=True, default='S/ 1,500')
    price_note = models.CharField('nota de precio', max_length=120, blank=True, default='incluido IGV')
    includes_text = models.TextField(
        'que incluye', blank=True,
        default='Incluye: table tent, dos sillas, WiFi, mantelería, conexión laptops, personal de logística.',
    )
    cta_label = models.CharField('texto del boton', max_length=120, blank=True, default='Registrarme a la rueda')

    class Meta:
        app_label = 'content'
        db_table = 'content_b2b_config'
        verbose_name = 'Configuración B2B'
        verbose_name_plural = 'Configuración B2B'

    def save(self, *args, **kwargs):
        self.pk = 1  # siempre la misma fila → singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Configuración B2B'


class B2BAgendaItem(TimeStampedModel):
    """Una fila de la agenda de la Rueda de Negocios B2B."""

    day_label = models.CharField('etiqueta del dia', max_length=80)
    title = models.CharField('actividad', max_length=200)
    time_range = models.CharField('horario', max_length=80, blank=True)
    is_active = models.BooleanField('activo', default=True)
    sort_order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        app_label = 'content'
        db_table = 'content_b2b_agenda_item'
        verbose_name = 'Agenda B2B'
        verbose_name_plural = 'Agenda B2B'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.day_label} — {self.title}'
