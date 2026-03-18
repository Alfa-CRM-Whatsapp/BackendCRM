from rest_framework import viewsets
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from core.crm.models import WhatsappMessage, WhatsappNumber, ContactWhatsapp, OutboundWhatsappMessage, Chat
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

            metadata = value.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id")

            whatsapp_number = WhatsappNumber.objects.get(
                phone_number_id=phone_number_id
            )

            # ==========================================
            # 📩 MENSAGEM RECEBIDA (INBOUND)
            # ==========================================
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

                # =========================
                # 🔥 GARANTE CHAT
                # =========================
                chat, _ = Chat.objects.get_or_create(
                    contact=contact,
                    from_number=whatsapp_number
                )

                # =========================
                # 💾 SALVA MENSAGEM
                # =========================
                WhatsappMessage.objects.create(
                    id_message=message_id,
                    type=message_type,
                    messaging_product=messaging_product,
                    contact=contact,
                    from_number=whatsapp_number,
                    chat=chat,  # 👈 AQUI
                    messages=message
                )

                print("📩 Mensagem recebida salva")

            # ==========================================
            # 📬 STATUS DE MENSAGEM ENVIADA (OUTBOUND)
            # ==========================================
            elif "statuses" in value:

                status_data = value["statuses"][0]

                message_id = status_data["id"]
                status_value = status_data["status"]

                updated = OutboundWhatsappMessage.objects.filter(
                    id_message=message_id
                ).update(
                    status=status_value
                )

                print(f"📬 Status atualizado: {message_id} -> {status_value} | updated={updated}")

            else:
                print("⚠️ Tipo de webhook desconhecido")

        except Exception as e:
            print("❌ Erro ao processar webhook:", str(e))

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

class RegisterWhatsappNumber(APIView):

    def post(self, request):

        phone = request.data["phone"]

        r = requests.post(
            f"https://graph.facebook.com/v19.0/{settings.WABA_ID}/phone_numbers",
            headers={
                "Authorization": f"Bearer {settings.ACESS_TOKEN}"
            },
            data={
                "cc": "55",
                "phone_number": phone,
                "verified_name": "CRM"
            }
        )

        data = r.json()

        if "id" not in data:
            return Response(data, status=400)

        number = WhatsappNumber.objects.create(
            phone=phone,
            phone_number_id=data["id"],
            verified=False
        )

        print(number + "Numero Criado")

        # solicitar código
        requests.post(
            f"https://graph.facebook.com/v19.0/{data['id']}/request_code",
            headers={
                "Authorization": f"Bearer {settings.META_TOKEN}"
            },
            data={"code_method": "SMS"}
        )

        return Response({
            "status": "code_sent",
            "phone_number_id": data["id"]
        })
    
class VerifyWhatsappNumber(APIView):

    def post(self, request):

        phone_number_id = request.data["phone_number_id"]
        code = request.data["code"]

        r = requests.post(
            f"https://graph.facebook.com/v19.0/{phone_number_id}/verify_code",
            headers={
                "Authorization": f"Bearer {settings.META_TOKEN}"
            },
            data={
                "code": code
            }
        )

        data = r.json()

        if data.get("success"):

            number = WhatsappNumber.objects.get(
                phone_number_id=phone_number_id
            )

            number.verified = True
            number.save()

        return Response(data)
    
class WhatsappConversationsByNumberView(APIView):

    def get(self, request, number_id):

        contacts = (
            WhatsappMessage.objects
            .filter(from_number_id=number_id)
            .select_related("contact", "from_number")
            .values(
                "contact__id",
                "contact__profile_name",
                "contact__number",
                "from_number__display_phone_number"
            )
            .distinct()
        )

        data = [
            {
                "contact_id": c["contact__id"],
                "profile_name": c["contact__profile_name"],
                "number_sender": c["contact__number"],
                "number_receive": c["from_number__display_phone_number"] 
            }
            for c in contacts
        ]

        return Response(data)