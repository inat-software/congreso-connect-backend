from django.urls import path

from apps.user.api.views import (
    AsistenteRegisterView,
    ExpositorRegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    MeView,
    SendMyQrView,
)

app_name = 'auth'

urlpatterns = [
    path('register/asistente/', AsistenteRegisterView.as_view(), name='register-asistente'),
    path('register/expositor/', ExpositorRegisterView.as_view(), name='register-expositor'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('me/send-qr/', SendMyQrView.as_view(), name='me-send-qr'),
]
