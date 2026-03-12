from rest_framework import viewsets
from core.crm.models import WhatsappNumber
from core.crm.serializers import WhatsappNumberSerializer

class WhatsappNumberView(viewsets.ModelViewSet):
    queryset = WhatsappNumber.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return WhatsappNumberSerializer
        return WhatsappNumberSerializer