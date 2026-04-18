# Routes

Este markdown é responsavel por expor todas as rotas e que seja possivel ver e entender o mapeamento completo de endpoints da API, incluindo rotas padrao geradas por viewsets e rotas customizadas.

```py
# Router (api/)
# Observacao: cada register gera rotas padrao de list/create/retrieve/update/destroy

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

# Rotas explicitas
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

## Indice de views

| Link | Oq e a view |
| --- | --- |
| [/api/users/](routes_detail/user_viewset.md) | `UserViewSet`: gestao de usuarios da aplicacao. |
| [/api/user-preferences/](routes_detail/user_preferences_viewset.md) | `UserPreferencesViewSet`: preferencias de usuario. |
| [/api/contacts/](routes_detail/contact_whatsapp_view.md) | `ContactWhatsappView`: CRUD de contatos WhatsApp. |
| [/api/messages/](routes_detail/whatsapp_message_view.md) | `WhatsappMessageView`: mensagens inbound e filtros. |
| [/api/messages/number/<int:number_id>/](routes_detail/whatsapp_message_by_number_view.md) | `WhatsappMessageByNumberView`: lista mensagens por numero. |
| [/api/messages/number/<int:number_id>/contact/<str:wa_id>/](routes_detail/whatsapp_message_by_number_and_contact_view.md) | `WhatsappMessageByNumberAndContactView`: mensagens por numero + contato. |
| [/api/sended-messages/](routes_detail/outbound_whatsapp_message_viewset.md) | `OutboundWhatsappMessageViewSet`: envio avulso e historico outbound. |
| [/api/numbers/](routes_detail/whatsapp_number_view.md) | `WhatsappNumberView`: CRUD de numeros WhatsApp. |
| [/api/verify-number/](routes_detail/verify_whatsapp_number.md) | `VerifyWhatsappNumber`: verificacao por codigo recebido. |
| [/api/register-number/](routes_detail/register_whatsapp_number.md) | `RegisterWhatsappNumber`: cadastro de numero e solicitacao de codigo. |
| [/api/register-number-on-meta/](routes_detail/register_whatsapp_number_on_meta.md) | `RegisterWhatsappNumberOnMeta`: registro final do numero na API da Meta. |
| [/api/chats/](routes_detail/chat_viewset.md) | `ChatViewSet`: gerenciamento de chats. |
| [/api/my-chats/](routes_detail/my_chats_viewset_list.md) | `MyChatsViewSet (list)`: chats relacionados ao usuario/contexto. |
| [/api/my-chats/by-contact/<int:contact_id>/](routes_detail/my_chats_viewset_by_contact.md) | `MyChatsViewSet (by_contact)`: chats filtrados por contato. |
| [/api/chat-window-validation/](routes_detail/chat_window_validation_view.md) | `ChatWindowValidationView`: valida janela de 24h da conversa. |
| [/api/templates/](routes_detail/whatsapp_template_viewset.md) | `WhatsAppTemplateViewSet`: CRUD de templates WhatsApp. |
| [/api/template-components/](routes_detail/template_component_viewset.md) | `TemplateComponentViewSet`: componentes de template. |
| [/api/template-parameters/](routes_detail/template_parameter_viewset.md) | `TemplateParameterViewSet`: parametros de template. |
| [/api/template-buttons/](routes_detail/template_button_viewset.md) | `TemplateButtonViewSet`: botoes de template. |
| [/api/template-submissions/](routes_detail/template_submission_viewset.md) | `TemplateSubmissionViewSet`: envios/submissoes de template para Meta. |
| [/api/send-template-message/](routes_detail/send_template_message_view.md) | `SendTemplateMessageView`: envio de mensagem usando template. |
| [/api/message-categories/](routes_detail/message_category_viewset.md) | `MessageCategoryViewSet`: categorias de mensagens. |
| [/api/category-examples/](routes_detail/category_example_viewset.md) | `CategoryExampleViewSet`: exemplos de categoria. |
| [/api/dispatches/](routes_detail/dispatch_viewset.md) | `DispatchViewSet`: historico e gerenciamento de disparos. |
| [/api/dispatch/](routes_detail/dispatch_direct_create.md) | `DispatchViewSet (create)`: disparo direto em chamada unica. |
| [/api/dispatch/<int:pk>/execute/](routes_detail/dispatch_execute.md) | `DispatchViewSet (execute)`: reexecucao de disparo existente. |
| [/api/webhook/whatsapp/](routes_detail/whatsapp_message_webhook_view.md) | `WhatsappMessageWebhookView`: recepcao de eventos/webhooks da Meta. |
| [/api/metrics/<str:metric_type>/](routes_detail/metrics_view.md) | `MetricsView`: endpoints de metricas. |
| [/api/superadmin-invites/](routes_detail/superadmin_invite_viewset.md) | `SuperAdminInviteViewSet`: convites de superadmin. |
| [/api/superadmin/approve/](routes_detail/approve_superadmin_invite_view.md) | `ApproveSuperAdminInviteView`: aprovacao de convite superadmin. |
| [/api/resend-token/](routes_detail/resend_superadmin_invite_token_view.md) | `ResendSuperAdminInviteTokenView`: reenvio de token de convite. |
| [/api/token/](routes_detail/email_token_obtain_pair_view.md) | `EmailTokenObtainPairView`: login e emissao de JWT. |
| [/api/token/refresh/](routes_detail/token_refresh_view.md) | `TokenRefreshView`: refresh de JWT. |
| [/api/schema/](routes_detail/spectacular_api_view.md) | `SpectacularAPIView`: schema OpenAPI da API. |
| [/api/docs/](routes_detail/spectacular_swagger_view.md) | `SpectacularSwaggerView`: documentacao Swagger UI. |
