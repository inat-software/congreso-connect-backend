from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class TicketType(TimeStampedModel):
    """A purchasable ticket tier for the event (e.g. General, Premium)."""

    class Currency(models.TextChoices):
        PEN = 'PEN', 'Sol peruano (S/)'   # default — Peru, listed first
        USD = 'USD', 'Dolar (US$)'

    name = models.CharField('nombre', max_length=120)
    description = models.TextField('descripcion', blank=True)
    price = models.DecimalField(
        'precio',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(
        'moneda',
        max_length=3,
        choices=Currency.choices,
        default=Currency.PEN,
    )
    is_popular = models.BooleanField('destacado', default=False)
    is_active = models.BooleanField('activo', default=True)
    capacity = models.PositiveIntegerField(
        'cupo', null=True, blank=True, help_text='Vacio = sin limite',
    )
    sort_order = models.PositiveIntegerField('orden', default=0)

    class Meta:
        app_label = 'tickets'
        db_table = 'tickets_ticket_type'
        verbose_name = 'Tipo de entrada'
        verbose_name_plural = 'Tipos de entrada'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.name} ({self.currency} {self.price})'
