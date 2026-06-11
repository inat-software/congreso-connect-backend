from rest_framework import serializers

from apps.content.models import (
    B2BAgendaItem,
    B2BConfig,
    Banner,
    EventConfig,
    Speaker,
    Sponsor,
)


EVENT_CONFIG_FIELDS = (
    'location_headline', 'location_description', 'dates', 'venue',
    'guest_country', 'previous_edition_label', 'previous_edition_stats',
    'map_query', 'contact_whatsapp_primary', 'contact_whatsapp_secondary',
    'contact_email', 'contact_address',
)


class EventConfigSerializer(serializers.ModelSerializer):
    """Configuración del evento (singleton). Lectura/edición para el admin."""

    class Meta:
        model = EventConfig
        fields = EVENT_CONFIG_FIELDS + ('updated_at',)
        read_only_fields = ('updated_at',)


class PublicEventConfigSerializer(serializers.ModelSerializer):
    """Configuración del evento para la landing (lectura pública)."""

    class Meta:
        model = EventConfig
        fields = EVENT_CONFIG_FIELDS
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
            'id', 'name', 'logo', 'logo_url', 'website', 'tier',
            'is_active', 'sort_order', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        # Debe quedar al menos una fuente de logo (archivo o URL).
        logo = attrs.get('logo', getattr(self.instance, 'logo', None))
        logo_url = attrs.get('logo_url', getattr(self.instance, 'logo_url', ''))
        if not logo and not logo_url:
            raise serializers.ValidationError(
                'Debes subir un logo o indicar una URL de logo.'
            )
        return attrs


class PublicSponsorSerializer(serializers.ModelSerializer):
    """Lightweight read-only serializer exposed to the public landing."""
    # `logo` = URL efectiva (externa si existe, si no el archivo subido).
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Sponsor
        fields = ('id', 'name', 'logo', 'website', 'tier')
        read_only_fields = fields

    def get_logo(self, obj):
        return obj.logo_display(self.context.get('request'))


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


B2B_CONFIG_FIELDS = (
    'eyebrow', 'title', 'description', 'card_title', 'price_label',
    'price', 'price_note', 'includes_text', 'cta_label',
)


class B2BConfigSerializer(serializers.ModelSerializer):
    """Config (singleton) de la Rueda B2B. Lectura/edición para el admin."""

    class Meta:
        model = B2BConfig
        fields = B2B_CONFIG_FIELDS + ('updated_at',)
        read_only_fields = ('updated_at',)


class PublicB2BConfigSerializer(serializers.ModelSerializer):
    """Config de la Rueda B2B para la landing (lectura pública)."""

    class Meta:
        model = B2BConfig
        fields = B2B_CONFIG_FIELDS
        read_only_fields = fields


class B2BAgendaItemSerializer(serializers.ModelSerializer):
    """Full read/write serializer for admin management."""

    class Meta:
        model = B2BAgendaItem
        fields = (
            'id', 'day_label', 'title', 'time_range',
            'is_active', 'sort_order', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PublicB2BAgendaItemSerializer(serializers.ModelSerializer):
    """Lightweight read-only serializer exposed to the public landing."""

    class Meta:
        model = B2BAgendaItem
        fields = ('id', 'day_label', 'title', 'time_range')
        read_only_fields = fields
