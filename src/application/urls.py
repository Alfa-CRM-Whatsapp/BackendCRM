from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from core.authentication.views import (
    EmailTokenObtainPairView,
    UserViewSet,
    CreateSuperAdminInviteView,
    ApproveSuperAdminInviteView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),

    path("api/token/", EmailTokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),

    path("api/superadmin/invite/", CreateSuperAdminInviteView.as_view()),
    path("api/superadmin/approve/<uuid:token>/", ApproveSuperAdminInviteView.as_view()),

    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

]