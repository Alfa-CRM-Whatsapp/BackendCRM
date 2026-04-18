# RegisterWhatsappNumber

- Route: /api/register-number/
- View: RegisterWhatsappNumber

## Codigo Da View

Fonte: src\core\crm\views\register_number.py

```python
import requests
from rest_framework.views import APIView
from core.crm.models import WhatsappNumber
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

class RegisterWhatsappNumber(APIView):
    def post(self, request):

        phone = request.data["phone"]
        phone_name = request.data.get("name", "CRM")
        phone_cc = request.data.get("cc", "55")
        language = request.data.get("language", "pt_BR")

        r = requests.post(
            f"https://graph.facebook.com/v25.0/{settings.BM_ID}/phone_numbers",
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
            waba_id=data["id"],
            name=phone_name,
            language=language,
            status="CODE_REQUESTED",
            verified=False
        )

        print(number.phone_number_id + "Numero Criado")

        rc = requests.post(
            f"https://graph.facebook.com/v25.0/{data['id']}/request_code",
            headers={
                "Authorization": f"Bearer {settings.ACCESS_TOKEN}"
            },
            data={
                "code_method": "SMS",
                "language": language,
            }
        )

        print(rc.json())

        return Response({
            "status": "code_sent",
            "phone_number_id": data["id"]
        })


class RegisterWhatsappNumberOnMeta(APIView):
    def post(self, request):
        phone_number_id = request.data.get("phone_number_id")
        pin = request.data.get("pin")

        if not phone_number_id:
            return Response(
                {"error": "phone_number_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pin:
            return Response(
                {"error": "pin é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = requests.post(
            f"https://graph.facebook.com/v25.0/{phone_number_id}/register",
            headers={
                "Authorization": f"Bearer {settings.ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "pin": str(pin),
            }
        )

        data = response.json()

        if response.status_code != 200:
            return Response(data, status=response.status_code)

        if data.get("success"):
            number = WhatsappNumber.objects.filter(phone_number_id=phone_number_id).first()
            if number:
                number.pin = str(pin)
                number.status = "REGISTERED"
                number.verified = True
                number.save(update_fields=["waba_id", "pin", "status", "verified"])

        return Response(data, status=status.HTTP_200_OK)
    

```

## Metodos Aceitos

### POST
- Registro Inicial E Solicitacao De Codigo: `POST /api/register-number/`
- Payload:
```json
{
  "phone": "11999999999",
  "name": "CRM",
  "cc": "55",
  "language": "pt_BR"
}
```

