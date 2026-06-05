from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para login.
    Inyecta claims adicionales en el access token (rol, nombre)
    y retorna datos del usuario en la respuesta.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Claims personalizados en el access token
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Datos adicionales en la respuesta JSON (no en el token)
        data['user'] = UserMinimalSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    """Serializer para logout — recibe el refresh token a invalidar."""
    refresh = serializers.CharField(help_text='Refresh token a invalidar.')

    def validate_refresh(self, value):
        try:
            self.token = RefreshToken(value)
        except Exception:
            raise serializers.ValidationError('Token de refresco invalido o expirado.')
        return value

    def save(self):
        self.token.blacklist()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Datos minimos del usuario para incluir en la respuesta de login."""
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'role', 'role_display', 'avatar')
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Serializer completo para lectura de usuarios."""
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'phone', 'is_active', 'avatar',
            'date_joined', 'last_login',
        )
        read_only_fields = ('id', 'full_name', 'role_display', 'date_joined', 'last_login')


class UserWriteSerializer(serializers.ModelSerializer):
    """Serializer para creacion/edicion de usuarios."""
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    # Permite enviar avatar='' para eliminar la foto
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'role', 'phone', 'is_active', 'password', 'avatar',
        )

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        new_avatar = validated_data.get('avatar', 'NOT_SET')

        # Si se envia avatar=None explicitamente, eliminar archivo anterior
        if new_avatar is None and instance.avatar:
            instance.avatar.delete(save=False)
            validated_data['avatar'] = None
        elif new_avatar == 'NOT_SET':
            # No se envio avatar — no tocar el existente
            validated_data.pop('avatar', None)
        elif new_avatar and instance.avatar:
            # Se sube nueva foto — eliminar la anterior del disco
            instance.avatar.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
