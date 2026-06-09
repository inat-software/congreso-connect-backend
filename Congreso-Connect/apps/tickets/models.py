from django.conf import settings
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


class Order(TimeStampedModel):
    """A purchase of a ticket tier by an attendee."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente de pago'
        PAID = 'paid', 'Pagada'
        CANCELLED = 'cancelled', 'Cancelada'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='usuario',
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='tipo de entrada',
    )

    # Snapshots: se copian al comprar y NO cambian aunque el admin edite o
    # borre el tipo de entrada despues (integridad del historial de compras).
    ticket_type_name = models.CharField('entrada', max_length=120)
    unit_price = models.DecimalField('precio unitario', max_digits=10, decimal_places=2)
    currency = models.CharField(
        'moneda', max_length=3, choices=TicketType.Currency.choices,
    )

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
        app_label = 'tickets'
        db_table = 'tickets_order'
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # El total siempre se deriva del snapshot (nunca se confia en el cliente).
        self.total_amount = (self.unit_price or 0) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Orden #{self.pk} — {self.ticket_type_name} x{self.quantity} ({self.get_status_display()})'
