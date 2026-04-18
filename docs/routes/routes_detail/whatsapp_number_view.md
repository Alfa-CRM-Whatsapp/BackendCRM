# WhatsappNumberView

- Route: /api/numbers/
- View: WhatsappNumberView

## Codigo Da View

Fonte: src\core\crm\views\number.py

```python
from rest_framework import viewsets
from core.crm.models import WhatsappNumber
from core.crm.serializers import WhatsappNumberSerializer

class WhatsappNumberView(viewsets.ModelViewSet):
    queryset = WhatsappNumber.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return WhatsappNumberSerializer
        return WhatsappNumberSerializer
```

## Metodos Aceitos

### GET
- Lista: `GET /api/numbers/`
- Detalhe: `GET /api/numbers/{id}/`

### POST
- Criacao: `POST /api/numbers/`
- Payload Minimo:
```json
{
  "display_phone_number": "5511999999999",
  "phone_number_id": "123456789",
  "name": "Numero Principal"
}
```

### PUT
- Atualizacao Completa: `PUT /api/numbers/{id}/`

### PATCH
- Atualizacao Parcial: `PATCH /api/numbers/{id}/`
- Exemplo:
```json
{
  "status": "VERIFIED",
  "verified": true
}
```

### DELETE
- Remocao: `DELETE /api/numbers/{id}/`

