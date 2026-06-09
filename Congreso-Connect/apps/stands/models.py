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
