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
