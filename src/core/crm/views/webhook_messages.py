import json

from django.conf import settings
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from core.crm.models import (
    WhatsappMessage,
    WhatsappNumber,
    ContactWhatsapp,
    OutboundWhatsappMessage,
    Chat,
    WhatsAppTemplate
)


class WhatsappMessageWebhookView(APIView):

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

            if field == "messages":

                metadata = value.get("metadata", {})
                phone_number_id = metadata.get("phone_number_id")

                whatsapp_number = WhatsappNumber.objects.get(
                    phone_number_id=phone_number_id
                )

                if "messages" in value:

                    message = value["messages"][0]
                    contact_data = value["contacts"][0]

                    contact_name = contact_data["profile"]["name"]
                    wa_id = contact_data["wa_id"]
                    number = message["from"]

                    message_id = message["id"]
                    message_type = message["type"]
                    messaging_product = value["messaging_product"]

                    contact, _ = ContactWhatsapp.objects.get_or_create(
                        wa_id=wa_id,
                        defaults={
                            "profile_name": contact_name,
                            "number": number,
                        }
                    )

                    chat, _ = Chat.objects.get_or_create(
                        contact=contact,
                        from_number=whatsapp_number
                    )

                    WhatsappMessage.objects.create(
                        id_message=message_id,
                        type=message_type,
                        messaging_product=messaging_product,
                        contact=contact,
                        from_number=whatsapp_number,
                        chat=chat,
                        messages=message
                    )

                    print("📨 Mensagem salva e enviada ao signal")

                elif "statuses" in value:

                    status_data = value["statuses"][0]

                    message_id = status_data["id"]
                    status_value = status_data["status"]

                    updated = OutboundWhatsappMessage.objects.filter(
                        id_message=message_id
                    ).update(
                        status=status_value
                    )

                    print(f"📬 Status atualizado: {message_id} -> {status_value}")

            elif field == "message_template_status_update":
                template_id = value.get("message_template_id")
                status = value.get("event")
                reason = value.get("reason")

                template = WhatsAppTemplate.objects.filter(
                    meta_template_id=template_id
                ).first()

                if template:
                    template.status = status

                    if status == "APPROVED":
                        template.approved_at = timezone.now()

                    if status == "REJECTED":
                        template.rejection_reason = reason

                    template.save()

                    print(f"📦 Template atualizado: {template.name} -> {status}")

            elif field == "template_category_update":

                template_id = value.get("message_template_id")
                new_category = value.get("new_category")

                template = WhatsAppTemplate.objects.filter(
                    meta_template_id=template_id
                ).first()

                if template and new_category:
                    template.category = new_category.lower()
                    template.save()

                    print(f"🔄 Categoria atualizada: {template.name} -> {new_category}")

        except Exception as e:
            print("❌ Erro ao processar webhook:", str(e))

        return JsonResponse({"status": "ok"})