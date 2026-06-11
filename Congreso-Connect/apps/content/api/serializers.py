from rest_framework import serializers

from apps.content.models import Banner, EventConfig, Speaker, Sponsor


class EventConfigSerializer(serializers.ModelSerializer):
    """Configuración del evento (singleton). Lectura/edición para el admin."""

    class Meta:
        model = EventConfig
        fields = (
            'location_headline', 'location_description', 'dates', 'venue',
            'guest_country', 'previous_edition_label', 'previous_edition_stats',
            'map_query', 'updated_at',
        )
        read_only_fields = ('updated_at',)


class PublicEventConfigSerializer(serializers.ModelSerializer):
    """Configuración del evento para la landing (lectura pública)."""

    class Meta:
        model = EventConfig
        fields = (
            'location_headline', 'location_description', 'dates', 'venue',
            'guest_country', 'previous_edition_label', 'previous_edition_stats',
            'map_query',
        )
        read_only_fields = fields


class SpeakerSerializer(serializers.ModelSerializer):
    """Full read/write serializer for admin management."""
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Speaker
        fields = (
            'id', 'name', 'role', 'position', 'bio', 'topic', 'photo',
            'is_active', 'sort_order', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PublicSpeakerSerializer(serializers.ModelSerializer):
    """Lightweight read-only serializer exposed to the public landing."""

    class Meta:
        model = Speaker
        fields = ('id', 'name', 'role', 'position', 'bio', 'topic', 'photo')
        read_only_fields = fields


class SponsorSerializer(serializers.ModelSerializer):
    """Full read/write serializer for admin management."""
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Sponsor
        fields = (
            'id', 'name', 'logo', 'website', 'tier',
            'is_active', 'sort_order', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PublicSponsorSerializer(serializers.ModelSerializer):
    """Lightweight read-only serializer exposed to the public landing."""

    class Meta:
        model = Sponsor
        fields = ('id', 'name', 'logo', 'website', 'tier')
        read_only_fields = fields


class BannerSerializer(serializers.ModelSerializer):
    """Full read/write serializer for admin management."""
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Banner
        fields = (
            'id', 'image', 'eyebrow', 'title', 'subtitle',
            'is_active', 'sort_order', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PublicBannerSerializer(serializers.ModelSerializer):
    """Lightweight read-only serializer exposed to the public landing."""

    class Meta:
        model = Banner
        fields = ('id', 'image', 'eyebrow', 'title', 'subtitle')
        read_only_fields = fields
