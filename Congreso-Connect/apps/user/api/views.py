from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
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
    AsistenteRegisterSerializer,
    CustomTokenObtainPairSerializer,
    ExpositorProfileAdminSerializer,
    ExpositorRegisterSerializer,
    LogoutSerializer,
    UserMinimalSerializer,
    UserSerializer,
    UserWriteSerializer,
    build_auth_response,
)
from apps.user.models import ExpositorProfile

User = get_user_model()


class AsistenteRegisterView(APIView):
    """
    POST /api/v1/auth/register/asistente/
    Auto-registro de un asistente/comprador. Crea la cuenta (rol 'user'),
    activa de inmediato, y devuelve tokens JWT (auto-login).
    """
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Registro de asistente',
        description='Crea una cuenta de asistente/comprador y retorna tokens JWT (auto-login).',
        request=AsistenteRegisterSerializer,
        responses={201: None},
        tags=['Autenticacion'],
    )
    def post(self, request):
        serializer = AsistenteRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), status=status.HTTP_201_CREATED)


class ExpositorRegisterView(APIView):
    """
    POST /api/v1/auth/register/expositor/
    Auto-registro de un expositor. Crea la cuenta (rol 'expositor') y su perfil
    en estado 'pendiente de aprobacion'. Devuelve tokens JWT (auto-login).
    """
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Registro de expositor',
        description='Crea una cuenta de expositor en estado pendiente de aprobacion y retorna tokens JWT (auto-login).',
        request=ExpositorRegisterSerializer,
        responses={201: None},
        tags=['Autenticacion'],
    )
    def post(self, request):
        serializer = ExpositorRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), status=status.HTTP_201_CREATED)


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


@extend_schema_view(
    list=extend_schema(summary='Listar expositores', tags=['Expositores']),
    retrieve=extend_schema(summary='Detalle de expositor', tags=['Expositores']),
)
class ExpositorProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Gestion de expositores para administradores: listar (filtrable por estado
    con ?status=pending|approved|rejected), aprobar y rechazar.

    SEGURIDAD: solo admin. La autorizacion se exige en el backend (nunca se
    confia en el frontend) — este recurso afecta a quien puede operar en el evento.
    """
    serializer_class = ExpositorProfileAdminSerializer
    permission_classes = (IsAuthenticated, IsAdminUser)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['razon_social', 'ruc', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'razon_social', 'approval_status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = ExpositorProfile.objects.select_related('user').all()
        status_param = self.request.query_params.get('status')
        if status_param in ExpositorProfile.ApprovalStatus.values:
            qs = qs.filter(approval_status=status_param)
        return qs

    def _set_status(self, new_status):
        profile = self.get_object()
        profile.approval_status = new_status
        profile.save(update_fields=['approval_status', 'updated_at'])
        return Response(self.get_serializer(profile).data)

    @extend_schema(summary='Aprobar expositor', tags=['Expositores'], request=None)
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        return self._set_status(ExpositorProfile.ApprovalStatus.APPROVED)

    @extend_schema(summary='Rechazar expositor', tags=['Expositores'], request=None)
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        return self._set_status(ExpositorProfile.ApprovalStatus.REJECTED)
