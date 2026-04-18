# ContactWhatsappView

- Route: /api/contacts/
- View: ContactWhatsappView

## Codigo Da View

Fonte: src\core\crm\views\contact.py

```python
from rest_framework import viewsets
from core.crm.models import ContactWhatsapp
from core.crm.serializers import ContactWhatsappListSerializer

class ContactWhatsappView(viewsets.ModelViewSet):
    queryset = ContactWhatsapp.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ContactWhatsappListSerializer
        return ContactWhatsappListSerializer
```

## Metodos Aceitos

### GET
- Lista: `GET /api/contacts/`
- Detalhe: `GET /api/contacts/{id}/`

### POST
- Criacao: `POST /api/contacts/`
- Payload:
```json
{
  "profile_name": "Cliente Teste",
  "wa_id": "5511999999999",
  "number": "5511999999999"
}
```

### PUT
- Atualizacao Completa: `PUT /api/contacts/{id}/`

### PATCH
- Atualizacao Parcial: `PATCH /api/contacts/{id}/`

### DELETE
- Remocao: `DELETE /api/contacts/{id}/`

