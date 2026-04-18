# VerifyWhatsappNumber

- Route: /api/verify-number/
- View: VerifyWhatsappNumber

## Codigo Da View

Fonte: src\core\crm\views\verify_number.py

```python
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
            f"https://graph.facebook.com/v25.0/{phone_number_id}/verify_code",
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
            number.status = "VERIFIED"
            number.save(update_fields=["verified", "status"])

        return Response(data)
    

```

## Metodos Aceitos

### POST
- Verificacao De Codigo: `POST /api/verify-number/`
- Payload:
```json
{
  "phone_number_id": "123456789",
  "code": "123456"
}
```

