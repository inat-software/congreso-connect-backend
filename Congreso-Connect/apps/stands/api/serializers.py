from django.db.models import Sum
from rest_framework import serializers

from apps.stands.models import StandReservation, StandType
from apps.user.api.serializers import UserMinimalSerializer


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


class StandReservationCreateSerializer(serializers.ModelSerializer):
    """
    Reserva de stand. El cliente solo envia stand_type_id + quantity. El precio
    lo pone el SERVIDOR desde el StandType real. Valida el cupo. La puerta de
    'solo expositor aprobado' se exige en la vista (permiso).
    """
    stand_type_id = serializers.PrimaryKeyRelatedField(
        source='stand_type',
        queryset=StandType.objects.all(),
        write_only=True,
    )

    class Meta:
        model = StandReservation
        fields = ('stand_type_id', 'quantity')

    def validate(self, attrs):
        stand_type = attrs['stand_type']
        quantity = attrs.get('quantity', 1)

        if not stand_type.is_active:
            raise serializers.ValidationError(
                {'stand_type_id': 'Este stand no esta disponible.'}
            )

        if stand_type.capacity is not None:
            reserved = (
                StandReservation.objects.filter(
                    stand_type=stand_type,
                    status__in=[StandReservation.Status.PENDING, StandReservation.Status.PAID],
                ).aggregate(total=Sum('quantity'))['total'] or 0
            )
            remaining = stand_type.capacity - reserved
            if quantity > remaining:
                raise serializers.ValidationError(
                    {'quantity': f'Cupo insuficiente. Quedan {max(remaining, 0)} stands.'}
                )
        return attrs

    def create(self, validated_data):
        stand_type = validated_data['stand_type']
        quantity = validated_data.get('quantity', 1)
        user = self.context['request'].user
        return StandReservation.objects.create(
            user=user,
            stand_type=stand_type,
            stand_type_name=stand_type.name,
            unit_price=stand_type.price,
            currency=stand_type.currency,
            quantity=quantity,
        )


class StandReservationSerializer(serializers.ModelSerializer):
    """Lectura de una reserva para el expositor (sus propias reservas)."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StandReservation
        fields = (
            'id', 'stand_type_name', 'unit_price', 'currency', 'quantity',
            'total_amount', 'status', 'status_display', 'paid_at', 'created_at',
        )
        read_only_fields = fields


class StandReservationAdminSerializer(serializers.ModelSerializer):
    """Lectura de reservas para el admin (incluye datos del expositor)."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = StandReservation
        fields = (
            'id', 'stand_type_name', 'unit_price', 'currency', 'quantity',
            'total_amount', 'status', 'status_display', 'paid_at',
            'user', 'created_at',
        )
        read_only_fields = fields
