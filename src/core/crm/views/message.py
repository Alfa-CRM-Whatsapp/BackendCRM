from rest_framework import viewsets
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from core.crm.models import WhatsappMessage, WhatsappNumber, ContactWhatsapp
from core.crm.serializers import WhatsappMessageListSerializer, WhatsappMessageCreateSerializer
import json
from django.conf import settings
from rest_framework.generics import ListAPIView

class WhatsappMessageView(viewsets.ModelViewSet):
    queryset = WhatsappMessage.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return WhatsappMessageListSerializer
        elif self.action == 'create':
            return WhatsappMessageCreateSerializer
        return WhatsappMessageListSerializer
    

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
            value = change["value"]

            metadata = value["metadata"]
            contacts = value["contacts"][0]
            message = value["messages"][0]

            # -----------------------------
            # Dados extraídos
            # -----------------------------

            phone_number_id = metadata["phone_number_id"]

            contact_name = contacts["profile"]["name"]
            wa_id = contacts["wa_id"]
            number = message["from"]

            message_id = message["id"]
            message_type = message["type"]
            messaging_product = value["messaging_product"]

            # -----------------------------
            # 1️⃣ Buscar ou criar contato
            # -----------------------------

            contact, created = ContactWhatsapp.objects.get_or_create(
                wa_id=wa_id,
                defaults={
                    "profile_name": contact_name,
                    "number": number,
                    "phone_number_id": phone_number_id,
                    "display_phone_number": number
                }
            )

            # -----------------------------
            # 2️⃣ Buscar número do WhatsApp
            # -----------------------------

            whatsapp_number = WhatsappNumber.objects.get(
                phone_number_id=phone_number_id
            )

            # -----------------------------
            # 3️⃣ Criar mensagem
            # -----------------------------

            WhatsappMessage.objects.create(
                id_message=message_id,
                type=message_type,
                messaging_product=messaging_product,
                contact=contact,
                messages=message,
                from_number=whatsapp_number
            )

        except Exception as e:
            print("Erro ao processar webhook:", str(e))

        return JsonResponse({"status": "ok"})

class WhatsappMessageByNumberView(ListAPIView):
    serializer_class = WhatsappMessageListSerializer

    def get_queryset(self):
        number_id = self.kwargs["number_id"]

        return WhatsappMessage.objects.filter(
            from_number_id=number_id
        ).select_related(
            "contact",
            "from_number"
        ).order_by("id")
    
class WhatsappMessageByNumberAndContactView(ListAPIView):
    serializer_class = WhatsappMessageListSerializer

    def get_queryset(self):
        number_id = self.kwargs["number_id"]
        wa_id = self.kwargs["wa_id"]

        return (
            WhatsappMessage.objects
            .filter(
                from_number_id=number_id,
                contact__wa_id=wa_id
            )
            .select_related("contact", "from_number")
            .order_by("id")
        )