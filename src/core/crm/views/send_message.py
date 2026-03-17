import requests
from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.response import Response

from core.crm.models import WhatsappNumber, OutboundWhatsappMessage
from core.crm.serializers import (
    OutboundWhatsappMessageListSerializer,
    OutboundWhatsappMessageCreateSerializer
)

class OutboundWhatsappMessageViewSet(viewsets.ModelViewSet):

    queryset = OutboundWhatsappMessage.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == "create":
            return OutboundWhatsappMessageCreateSerializer
        return OutboundWhatsappMessageListSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        contact = serializer.validated_data.get("contact")
        whatsapp_number = serializer.validated_data["from_number"]
        message_text = serializer.validated_data["message_text"]
        breakpoint()
        if not contact:
            return Response(
                {"error": "O campo 'contact' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        to = contact.number
        phone_number_id = whatsapp_number.phone_number_id

        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

        headers = {
            "Authorization": f"Bearer {settings.ACESS_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message_text
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code != 200:
                return Response(response_data, status=response.status_code)

            message_id = response_data["messages"][0]["id"]

            message = OutboundWhatsappMessage.objects.create(
                id_message=message_id,
                contact=contact,
                from_number=whatsapp_number,
                message_text=message_text,
                status="sent",
                raw_response=response_data
            )

            return Response({
                "message": "Mensagem enviada com sucesso",
                "data": OutboundWhatsappMessageListSerializer(message).data
            }, status=status.HTTP_201_CREATED)

        except WhatsappNumber.DoesNotExist:
            return Response(
                {"error": "Número de WhatsApp não cadastrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )