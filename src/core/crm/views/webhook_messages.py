import json

from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from core.crm.views.webhook import (
    handle_account_update_field,
    handle_messages_field,
    handle_template_category_update,
    handle_template_status_update,
)

class WhatsappMessageWebhookView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            return HttpResponse(challenge)

        return HttpResponse("Token inválido", status=403)

    def post(self, request):
        data = request.data

        print("WEBHOOK RECEBIDO:", json.dumps(data, indent=2))

        try:
            entry = data["entry"][0]
            change = entry["changes"][0]

            field = change.get("field")
            value = change.get("value", {})

            field_handlers = {
                "messages": handle_messages_field,
                "account_update": handle_account_update_field,
                "message_template_status_update": handle_template_status_update,
                "template_category_update": handle_template_category_update,
            }

            handler = field_handlers.get(field)

            if handler:
                if field == "account_update":
                    handler(value, entry.get("id"))
                else:
                    handler(value)

            return JsonResponse({"status": "ok"})

        except Exception as e:
            print("❌ Erro ao processar webhook:", str(e))

        return JsonResponse({"status": "ok"})