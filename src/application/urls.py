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

from core.crm.views import (
    ContactWhatsappView,
    WhatsappMessageView,
    WhatsappMessageWebhookView,
    WhatsappNumberView,
    WhatsappMessageByNumberView,
    WhatsappMessageByNumberAndContactView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'contacts', ContactWhatsappView, basename='contact')
router.register(r'messages', WhatsappMessageView, basename='message')
router.register(r'numbers', WhatsappNumberView, basename='number')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),

    path("api/token/", EmailTokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),

    path("api/superadmin/invite/", CreateSuperAdminInviteView.as_view()),
    path("api/superadmin/approve/", ApproveSuperAdminInviteView.as_view()),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("api/webhook/whatsapp/", WhatsappMessageWebhookView.as_view(), name="whatsapp-webhook"),

      path(
        "api/messages/number/<int:number_id>/",
        WhatsappMessageByNumberView.as_view()
    ),

    path(
        "api/messages/number/<int:number_id>/contact/<str:wa_id>/",
        WhatsappMessageByNumberAndContactView.as_view(),
    ),
]