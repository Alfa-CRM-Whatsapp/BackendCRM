from rest_framework import viewsets
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from core.crm.models import WhatsappMessage, WhatsappNumber, ContactWhatsapp
from core.crm.serializers import WhatsappMessageListSerializer, WhatsappMessageCreateSerializer
import json
from django.conf import settings
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
import requests

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

class WhatsappEmbeddedSignupCallbackView(APIView):

    def get(self, request):

        code = request.GET.get("code")

        if not code:
            return Response({"error": "code não encontrado"}, status=400)

        # 1️⃣ trocar code por access_token
        token_response = requests.get(
            "https://graph.facebook.com/v19.0/oauth/access_token",
            params={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "redirect_uri": settings.META_REDIRECT_URI,
                "code": code,
            },
        )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return Response({"error": token_data}, status=400)

        # 2️⃣ buscar businesses do usuário
        businesses = requests.get(
            "https://graph.facebook.com/v19.0/me/businesses",
            params={"access_token": access_token},
        ).json()

        business_id = businesses["data"][0]["id"]

        # 3️⃣ buscar WABA
        waba = requests.get(
            f"https://graph.facebook.com/v19.0/{business_id}/owned_whatsapp_business_accounts",
            params={"access_token": access_token},
        ).json()

        waba_id = waba["data"][0]["id"]

        # 4️⃣ buscar números
        numbers = requests.get(
            f"https://graph.facebook.com/v19.0/{waba_id}/phone_numbers",
            params={"access_token": access_token},
        ).json()

        saved_numbers = []

        for number in numbers["data"]:

            obj, created = WhatsappNumber.objects.update_or_create(
                phone_number_id=number["id"],
                defaults={
                    "display_phone_number": number["display_phone_number"],
                    "name": number.get("verified_name", "WhatsApp")
                }
            )

            saved_numbers.append(obj.id)

        return Response({
            "status": "connected",
            "numbers_saved": saved_numbers
        })