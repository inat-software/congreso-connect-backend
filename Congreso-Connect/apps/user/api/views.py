from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.core.permissions import IsAdminUser
from apps.user.api.filters import UserFilter
from apps.user.api.serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    UserMinimalSerializer,
    UserSerializer,
    UserWriteSerializer,
)

User = get_user_model()


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Autentica al usuario con email y password.
    Retorna access token, refresh token y datos basicos del usuario.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Iniciar sesion',
        description='Autentica con email y password. Retorna tokens JWT y datos del usuario.',
        tags=['Autenticacion'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    """
    POST /api/v1/auth/refresh/
    Refresca el access token usando un refresh token valido.
    Con ROTATE_REFRESH_TOKENS=True, tambien emite un nuevo refresh token.
    """
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Refrescar token',
        description='Emite un nuevo access token (y refresh token rotado) a partir del refresh token actual.',
        tags=['Autenticacion'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Invalida el refresh token (blacklist) para cerrar la sesion.
    """
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Cerrar sesion',
        description='Invalida el refresh token enviado, impidiendo su reutilizacion.',
        request=LogoutSerializer,
        responses={205: None},
        tags=['Autenticacion'],
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Sesion cerrada correctamente.'},
            status=status.HTTP_205_RESET_CONTENT,
        )


class MeView(APIView):
    """
    GET /api/v1/auth/me/
    Retorna los datos del usuario autenticado actual.
    Util para verificar la sesion desde el frontend.
    """
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Usuario actual',
        description='Retorna los datos del usuario autenticado.',
        responses=UserMinimalSerializer,
        tags=['Autenticacion'],
    )
    def get(self, request):
        serializer = UserMinimalSerializer(request.user)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='Listar usuarios', tags=['Usuarios']),
    retrieve=extend_schema(summary='Detalle de usuario', tags=['Usuarios']),
    create=extend_schema(summary='Crear usuario', tags=['Usuarios']),
    partial_update=extend_schema(summary='Editar usuario', tags=['Usuarios']),
    destroy=extend_schema(summary='Eliminar usuario', tags=['Usuarios']),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de usuarios.
    Solo accesible por administradores.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'email', 'last_name', 'role']
    ordering = ['-date_joined']

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return UserWriteSerializer
        return UserSerializer

    def get_permissions(self):
        return [IsAuthenticated(), IsAdminUser()]
