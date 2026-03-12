from rest_framework import viewsets
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from core.crm.models import WhatsappMessage
from core.crm.serializers import WhatsappMessageListSerializer, WhatsappMessageCreateSerializer
import json
from django.conf import settings

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

        with open("/tmp/webhook_log.txt", "a") as f:
            f.write(json.dumps(data, indent=2) + "\n---\n")

        print("WEBHOOK RECEBIDO:", json.dumps(data, indent=2))

        return JsonResponse({"status": "ok"})