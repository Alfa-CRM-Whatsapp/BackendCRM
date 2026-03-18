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
    ApproveSuperAdminInviteView,
    SuperAdminInviteViewSet,
    UserPreferencesViewSet
)

from core.crm.views import (
    ContactWhatsappView,
    WhatsappMessageView,
    WhatsappMessageWebhookView,
    WhatsappNumberView,
    WhatsappMessageByNumberView,
    WhatsappMessageByNumberAndContactView,
    VerifyWhatsappNumber,
    RegisterWhatsappNumber,
    OutboundWhatsappMessageViewSet,
    ChatViewSet,
    MyChatsViewSet,
    WhatsappMessageWebhookView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'user-preferences', UserPreferencesViewSet, basename='user-preferences')
router.register(r'contacts', ContactWhatsappView, basename='contact')
router.register(r'messages', WhatsappMessageView, basename='message')
router.register(r'numbers', WhatsappNumberView, basename='number')
router.register(r'sended-messages', OutboundWhatsappMessageViewSet, basename='sended-message')
router.register(r'superadmin-invites', SuperAdminInviteViewSet, basename='superadmin-invite')
router.register(r'chats', ChatViewSet, basename='chat')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path("api/token/", EmailTokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/superadmin/approve/", ApproveSuperAdminInviteView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/webhook/whatsapp/", WhatsappMessageWebhookView.as_view(), name="whatsapp-webhook"),
    path("api/messages/number/<int:number_id>/", WhatsappMessageByNumberView.as_view()),
    path("api/messages/number/<int:number_id>/contact/<str:wa_id>/", WhatsappMessageByNumberAndContactView.as_view()),
    path("api/verify-number/", VerifyWhatsappNumber.as_view()),
    path("api/register-number/", RegisterWhatsappNumber.as_view()),
    path("api/my-chats/", MyChatsViewSet.as_view({"get": "list"}), name="my-chats"),
]