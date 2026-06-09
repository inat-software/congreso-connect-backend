from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class StandType(TimeStampedModel):
    """A type of exhibition stand offered at the fair (e.g. 6 m², 16 m²)."""

    class Currency(models.TextChoices):
        PEN = 'PEN', 'Sol peruano (S/)'
        USD = 'USD', 'Dolar (US$)'

    name = models.CharField('nombre', max_length=120)
    dimensions = models.CharField('dimensiones', max_length=150, blank=True)
    price = models.DecimalField(
        'precio', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
    )
    currency = models.CharField(
        'moneda', max_length=3, choices=Currency.choices, default=Currency.PEN,
    )
    price_plus_igv = models.BooleanField('precio + IGV', default=True)
    includes = models.TextField('que incluye', blank=True, help_text='Un item por linea')
    capacity = models.PositiveIntegerField(
        'cupo (stands disponibles)', null=True, blank=True, help_text='Vacio = sin limite',
    )
    is_active = models.BooleanField('activo', default=True)
    sort_order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        app_label = 'stands'
        db_table = 'stands_stand_type'
        verbose_name = 'Tipo de stand'
        verbose_name_plural = 'Tipos de stand'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.name} ({self.currency} {self.price})'


class StandReservation(TimeStampedModel):
    """An approved exhibitor's reservation of a stand."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente de pago'
        PAID = 'paid', 'Pagada'
        CANCELLED = 'cancelled', 'Cancelada'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stand_reservations',
        verbose_name='expositor',
    )
    stand_type = models.ForeignKey(
        StandType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
        verbose_name='tipo de stand',
    )

    # Snapshots: se copian al reservar y NO cambian aunque el admin edite o
    # borre el tipo de stand despues.
    stand_type_name = models.CharField('stand', max_length=120)
    unit_price = models.DecimalField('precio unitario', max_digits=10, decimal_places=2)
    currency = models.CharField('moneda', max_length=3, choices=StandType.Currency.choices)

    quantity = models.PositiveIntegerField(
        'cantidad', default=1, validators=[MinValueValidator(1)],
    )
    total_amount = models.DecimalField('total', max_digits=12, decimal_places=2)

    status = models.CharField(
        'estado', max_length=20, choices=Status.choices,
        default=Status.PENDING, db_index=True,
    )
    paid_at = models.DateTimeField('pagada el', null=True, blank=True)

    class Meta:
        app_label = 'stands'
        db_table = 'stands_reservation'
        verbose_name = 'Reserva de stand'
        verbose_name_plural = 'Reservas de stand'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.total_amount = (self.unit_price or 0) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Reserva #{self.pk} — {self.stand_type_name} x{self.quantity} ({self.get_status_display()})'
