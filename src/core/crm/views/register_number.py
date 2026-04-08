import requests
from rest_framework.views import APIView
from core.crm.models import WhatsappNumber
from django.conf import settings
from rest_framework.response import Response

class RegisterWhatsappNumber(APIView):

    def post(self, request):

        phone = request.data["phone"]

        r = requests.post(
            f"https://graph.facebook.com/v19.0/{settings.WABA_ID}/phone_numbers",
            headers={
                "Authorization": f"Bearer {settings.ACCESS_TOKEN}"
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
    
