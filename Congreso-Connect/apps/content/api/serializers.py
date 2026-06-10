from rest_framework import serializers

from apps.content.models import Speaker


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
