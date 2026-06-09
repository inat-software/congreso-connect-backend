from rest_framework import serializers

from apps.stands.models import StandType


class StandTypeSerializer(serializers.ModelSerializer):
    """Full read/write serializer for admin management."""
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)

    class Meta:
        model = StandType
        fields = (
            'id', 'name', 'dimensions', 'price', 'currency', 'currency_display',
            'price_plus_igv', 'includes', 'capacity', 'is_active', 'sort_order',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'currency_display', 'created_at', 'updated_at')


class PublicStandTypeSerializer(serializers.ModelSerializer):
    """Lightweight read-only serializer exposed to the public landing."""

    class Meta:
        model = StandType
        fields = (
            'id', 'name', 'dimensions', 'price', 'currency',
            'price_plus_igv', 'includes',
        )
        read_only_fields = fields
