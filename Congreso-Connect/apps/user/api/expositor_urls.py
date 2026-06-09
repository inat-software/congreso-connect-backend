from rest_framework.routers import DefaultRouter

from apps.user.api.views import ExpositorProfileViewSet

router = DefaultRouter()
router.register('', ExpositorProfileViewSet, basename='expositores')

urlpatterns = router.urls
