from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
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

        url = f"https://graph.facebook.com/v23.0/{settings.PHONE_NUMBER_ID}/messages"

        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        return Response({
            "meta_status": response.status_code,
            "meta_response": response.json(),
            "payload_sent": payload
        }, status=200)