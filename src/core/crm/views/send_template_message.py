from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import uuid
import requests
from core.crm.models import Chat, OutboundWhatsappMessage, WhatsappNumber
from core.crm.serializers import OutboundWhatsappMessageListSerializer
from core.crm.serializers import SendTemplateMessageSerializer

def build_send_components(template, parameters: dict):
    components = []

    for comp in template.components.all().order_by("order"):
        if comp.type != "body":
            continue

        params = []

        for p in comp.parameters.all().order_by("order"):
            value = parameters.get(p.name)

            if not value:
                raise ValueError(f"Parâmetro '{p.name}' não enviado")

            params.append({
                "type": "text",
                "parameter_name": p.name,
                "text": value
            })

        components.append({
            "type": "body",
            "parameters": params
        })

    return components

class SendTemplateMessageView(APIView):

    def post(self, request):
        serializer = SendTemplateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact = serializer.validated_data["contact_obj"]
        template = serializer.validated_data["template_obj"]
        parameters = serializer.validated_data.get("parameters", {})
        from_number = serializer.validated_data["from_number_obj"]

        try:
            components = build_send_components(template, parameters)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        payload = {
            "messaging_product": "whatsapp",
            "to": contact.number,
            "type": "template",
            "template": {
                "name": template.name,
                "language": {
                    "code": template.language
                },
                "components": components
            }
        }

        url = f"https://graph.facebook.com/v250/{from_number.phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {settings.ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        response_data = response.json()

        if response.status_code != 200:
            return Response({
                "meta_status": response.status_code,
                "meta_response": response_data,
                "payload_sent": payload
            }, status=response.status_code)

        chat, _ = Chat.objects.get_or_create(
            contact=contact,
            from_number=from_number,
        )

        message_id = response_data.get("messages", [{}])[0].get("id") or f"template-send-{uuid.uuid4().hex}"

        outbound = OutboundWhatsappMessage.objects.create(
            id_message=message_id,
            contact=contact,
            from_number=from_number,
            chat=chat,
            message=payload,
            status="sent",
            with_template=True,
            raw_response=response_data,
        )

        return Response({
            "meta_status": response.status_code,
            "meta_response": response_data,
            "payload_sent": payload,
            "data": OutboundWhatsappMessageListSerializer(outbound).data,
        }, status=200)