# WhatsappMessageView

- Route: /api/messages/
- View: WhatsappMessageView

## Codigo Da View

Fonte: src\core\crm\views\message.py

```python
import requests
from rest_framework import viewsets
from rest_framework.views import APIView
from core.crm.models import WhatsappMessage
from core.crm.serializers import WhatsappMessageListSerializer, WhatsappMessageCreateSerializer
from django.conf import settings
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from core.crm.filters import WhatsappMessageFilter, WhatsappMessageByNumberFilter
from django_filters.rest_framework import DjangoFilterBackend

class WhatsappMessageView(viewsets.ModelViewSet):
    queryset = WhatsappMessage.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = WhatsappMessageFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return WhatsappMessageListSerializer
        elif self.action == 'create':
            return WhatsappMessageCreateSerializer
        return WhatsappMessageListSerializer
    
class WhatsappMessageByNumberView(ListAPIView):
    serializer_class = WhatsappMessageListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WhatsappMessageByNumberFilter

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
    filter_backends = [DjangoFilterBackend]
    filterset_class = WhatsappMessageByNumberFilter

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
  

```

## Metodos Aceitos

### GET
- Lista: `GET /api/messages/`
- Query Params:
- `category`: Um ou mais nomes de categoria.
- `year`: Ano de criacao.
- `month`: Mes de criacao.
- `day`: Dia de criacao.

### POST
- Criacao: `POST /api/messages/`
- Payload:
```json
{
  "id_message": "wamid.XXX",
  "type": "text",
  "messaging_product": "whatsapp",
  "contact": 1,
  "from_number": 1,
  "messages": {
    "text": {"body": "Ola"}
  }
}
```

### PUT
- Atualizacao Completa: `PUT /api/messages/{id}/`

### PATCH
- Atualizacao Parcial: `PATCH /api/messages/{id}/`

### DELETE
- Remocao: `DELETE /api/messages/{id}/`

