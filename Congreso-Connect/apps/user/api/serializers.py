from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import translation
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import ExpositorProfile

User = get_user_model()


def spanish_password_validator(value):
    """
    Valida la contrasena con los validadores de Django, devolviendo los mensajes
    en espanol y como error del propio campo (no en non_field_errors).
    """
    try:
        with translation.override('es'):
            validate_password(value)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(list(exc.messages))


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


def build_auth_response(user):
    """
    Genera tokens JWT (auto-login) + datos del usuario.
    Mismo formato que la respuesta de login para que el frontend lo trate igual.
    """
    refresh = CustomTokenObtainPairSerializer.get_token(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserMinimalSerializer(user).data,
    }


class AsistenteRegisterSerializer(serializers.ModelSerializer):
    """
    Auto-registro de ASISTENTE / comprador. Crea una cuenta activa de inmediato.
    El rol se fuerza a 'user' en el servidor: NUNCA se acepta desde el cliente.
    """
    password = serializers.CharField(
        write_only=True, min_length=8, validators=[spanish_password_validator],
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = User.Role.USER
        return User.objects.create_user(password=password, **validated_data)


class ExpositorRegisterSerializer(serializers.Serializer):
    """
    Auto-registro de EXPOSITOR. Crea el usuario (rol 'expositor') y su
    ExpositorProfile en estado 'pendiente de aprobacion'. Un administrador
    debera aprobarlo despues. El rol se fuerza en el servidor.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, min_length=8, validators=[spanish_password_validator],
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    razon_social = serializers.CharField(max_length=255)
    ruc = serializers.CharField(max_length=20)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        profile_data = {
            'razon_social': validated_data.pop('razon_social'),
            'ruc': validated_data.pop('ruc'),
        }
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            role=User.Role.EXPOSITOR,
            **validated_data,
        )
        ExpositorProfile.objects.create(user=user, **profile_data)
        return user


class UserMinimalSerializer(serializers.ModelSerializer):
    """Datos minimos del usuario para incluir en la respuesta de login."""
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    # Estado de aprobacion del expositor (None si el usuario no es expositor).
    # Permite al frontend decidir a donde redirigir tras el login.
    expositor_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'expositor_status', 'phone', 'avatar',
        )
        read_only_fields = fields

    def get_expositor_status(self, obj):
        profile = getattr(obj, 'expositor_profile', None)
        return profile.approval_status if profile else None


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


class MeUpdateSerializer(serializers.ModelSerializer):
    """
    Edicion del PROPIO perfil del usuario autenticado (no de otros).
    Permite cambiar nombre, telefono y avatar. Para cambiar la contrasena se
    exige la contrasena actual (buena practica: el atacante con una sesion
    robada no puede cambiarla sin conocer la actual).
    """
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'avatar',
            'current_password', 'new_password',
        )

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        if new_password:
            user = self.instance
            current = attrs.get('current_password')
            if not current or not user.check_password(current):
                raise serializers.ValidationError(
                    {'current_password': 'La contrasena actual es incorrecta.'}
                )
            # Mensajes en espanol y asociados al campo 'new_password' (no a
            # non_field_errors), para que el frontend muestre el error claro.
            try:
                with translation.override('es'):
                    validate_password(new_password, user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({'new_password': list(exc.messages)})
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)

        # Manejo de avatar: si llega None explicito, borrar; si llega uno nuevo,
        # eliminar el anterior del disco; si no llega, no tocar.
        new_avatar = validated_data.get('avatar', 'NOT_SET')
        if new_avatar is None and instance.avatar:
            instance.avatar.delete(save=False)
            validated_data['avatar'] = None
        elif new_avatar == 'NOT_SET':
            validated_data.pop('avatar', None)
        elif new_avatar and instance.avatar:
            instance.avatar.delete(save=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance


class ExpositorProfileAdminSerializer(serializers.ModelSerializer):
    """Lectura de perfiles de expositor para la gestion del administrador."""
    user = UserMinimalSerializer(read_only=True)
    approval_status_display = serializers.CharField(
        source='get_approval_status_display', read_only=True,
    )

    class Meta:
        model = ExpositorProfile
        fields = (
            'id', 'razon_social', 'ruc',
            'approval_status', 'approval_status_display',
            'user', 'created_at', 'updated_at',
        )
        read_only_fields = fields
