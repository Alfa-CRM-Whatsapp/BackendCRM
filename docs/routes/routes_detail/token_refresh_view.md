# TokenRefreshView

- Route: /api/token/refresh/
- View: TokenRefreshView

## Codigo Da View

Fonte: src\application\urls.py

```python
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
    UserPreferencesViewSet,
    ResendSuperAdminInviteTokenView
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
    RegisterWhatsappNumberOnMeta,
    OutboundWhatsappMessageViewSet,
    ChatViewSet,
    ChatWindowValidationView,
    MyChatsViewSet,
    WhatsappMessageWebhookView,
    WhatsAppTemplateViewSet,
    TemplateComponentViewSet,
    TemplateParameterViewSet,
    TemplateButtonViewSet,
    TemplateSubmissionViewSet,
    SendTemplateMessageView,
    MessageCategoryViewSet,
    CategoryExampleViewSet,
    MetricsView,
    DispatchViewSet,
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
router.register(r'templates', WhatsAppTemplateViewSet, basename='template')
router.register(r'template-components', TemplateComponentViewSet, basename='template-component')
router.register(r'template-parameters', TemplateParameterViewSet, basename='template-parameter')
router.register(r'template-buttons', TemplateButtonViewSet, basename='template-button')
router.register(r'template-submissions', TemplateSubmissionViewSet, basename='template-submission')
router.register(r'message-categories', MessageCategoryViewSet, basename='message-category')
router.register(r'category-examples', CategoryExampleViewSet, basename='category-example')
router.register(r'dispatches', DispatchViewSet, basename='dispatch')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dispatch/', DispatchViewSet.as_view({'post': 'create'}), name='dispatch-direct-create'),
    path('api/dispatch/<int:pk>/execute/', DispatchViewSet.as_view({'post': 'execute'}), name='dispatch-direct-execute'),
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
    path("api/register-number-on-meta/", RegisterWhatsappNumberOnMeta.as_view()),
    path("api/my-chats/", MyChatsViewSet.as_view({"get": "list"}), name="my-chats"),
    path("api/my-chats/by-contact/<int:contact_id>/", MyChatsViewSet.as_view({"get": "by_contact"}), name="my-chats-by-contact"),
    path("api/chat-window-validation/", ChatWindowValidationView.as_view(), name="chat-window-validation"),
    path('api/resend-token/', ResendSuperAdminInviteTokenView.as_view(), name='resend-token'),
    path('api/send-template-message/', SendTemplateMessageView.as_view(), name='send-template-message'),
    path('api/metrics/<str:metric_type>/', MetricsView.as_view(), name='metrics'),
]
```
