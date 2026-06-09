from django.db.models import Sum
from rest_framework import serializers

from apps.tickets.models import Order, TicketType
from apps.user.api.serializers import UserMinimalSerializer


class TicketTypeSerializer(serializers.ModelSerializer):
    """Full read/write serializer for admin management."""
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)

    class Meta:
        model = TicketType
        fields = (
            'id', 'name', 'description', 'price', 'currency', 'currency_display',
            'is_popular', 'is_active', 'capacity', 'sort_order',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'currency_display', 'created_at', 'updated_at')


class PublicTicketTypeSerializer(serializers.ModelSerializer):
    """Lightweight read-only serializer exposed to the public landing."""

    class Meta:
        model = TicketType
        fields = ('id', 'name', 'description', 'price', 'currency', 'is_popular')
        read_only_fields = fields


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Compra de entradas. El cliente SOLO envia ticket_type_id + quantity.
    El precio, la moneda y el nombre los pone el SERVIDOR desde el TicketType
    real (nunca se confia en un precio enviado por el cliente). Valida el cupo.
    """
    ticket_type_id = serializers.PrimaryKeyRelatedField(
        source='ticket_type',
        queryset=TicketType.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Order
        fields = ('ticket_type_id', 'quantity')

    def validate(self, attrs):
        ticket_type = attrs['ticket_type']
        quantity = attrs.get('quantity', 1)

        if not ticket_type.is_active:
            raise serializers.ValidationError(
                {'ticket_type_id': 'Esta entrada no esta disponible.'}
            )

        # Control de cupo: cuenta lo ya reservado (pendiente + pagada).
        if ticket_type.capacity is not None:
            reserved = (
                Order.objects.filter(
                    ticket_type=ticket_type,
                    status__in=[Order.Status.PENDING, Order.Status.PAID],
                ).aggregate(total=Sum('quantity'))['total'] or 0
            )
            remaining = ticket_type.capacity - reserved
            if quantity > remaining:
                raise serializers.ValidationError(
                    {'quantity': f'Cupo insuficiente. Quedan {max(remaining, 0)} entradas.'}
                )
        return attrs

    def create(self, validated_data):
        ticket_type = validated_data['ticket_type']
        quantity = validated_data.get('quantity', 1)
        user = self.context['request'].user
        return Order.objects.create(
            user=user,
            ticket_type=ticket_type,
            ticket_type_name=ticket_type.name,
            unit_price=ticket_type.price,
            currency=ticket_type.currency,
            quantity=quantity,
        )


class OrderSerializer(serializers.ModelSerializer):
    """Lectura de una orden para el comprador (sus propias ordenes)."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'ticket_type_name', 'unit_price', 'currency', 'quantity',
            'total_amount', 'status', 'status_display', 'paid_at', 'created_at',
        )
        read_only_fields = fields


class OrderAdminSerializer(serializers.ModelSerializer):
    """Lectura de ordenes para el admin (incluye datos del comprador)."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'ticket_type_name', 'unit_price', 'currency', 'quantity',
            'total_amount', 'status', 'status_display', 'paid_at',
            'user', 'created_at',
        )
        read_only_fields = fields
