import requests
from rest_framework.views import APIView
from core.crm.models import WhatsappNumber
from django.conf import settings
from rest_framework.response import Response

class RegisterWhatsappNumber(APIView):
    def post(self, request):

        phone = request.data["phone"]
        phone_name = request.data.get("name", "CRM")
        phone_cc = request.data.get("cc", "55")

        r = requests.post(
            f"https://graph.facebook.com/v19.0/{settings.WABA_ID}/phone_numbers",
            headers={
                "Authorization": f"Bearer {settings.ACCESS_TOKEN}"
            },
            data={
                "cc": phone_cc,
                "phone_number": phone,
                "verified_name": phone_name
            }
        )

        data = r.json()

        if "id" not in data:
            return Response(data, status=400)

        number = WhatsappNumber.objects.create(
            display_phone_number=phone,
            phone_number_id=data["id"],
            name=phone_name,
            verified=False
        )

        print(number.phone_number_id + "Numero Criado")

        rc = requests.post(
            f"https://graph.facebook.com/v19.0/{data['id']}/request_code",
            headers={
                "Authorization": f"Bearer {settings.ACCESS_TOKEN}"
            },
            data={"code_method": "SMS"}
        )

        print(rc.json())

        return Response({
            "status": "code_sent",
            "phone_number_id": data["id"]
        })
    
