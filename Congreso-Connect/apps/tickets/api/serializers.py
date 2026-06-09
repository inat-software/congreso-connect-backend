from rest_framework import serializers

from apps.tickets.models import TicketType


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
