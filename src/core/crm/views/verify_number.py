import requests
from rest_framework.views import APIView
from core.crm.models import WhatsappNumber
from django.conf import settings
from rest_framework.response import Response

class VerifyWhatsappNumber(APIView):
    def post(self, request):
        phone_number_id = request.data["phone_number_id"]
        code = request.data["code"]

        r = requests.post(
            f"https://graph.facebook.com/v19.0/{phone_number_id}/verify_code",
            headers={
                "Authorization": f"Bearer {settings.ACCESS_TOKEN}",
                "Content-Type": "application/json"
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
    
