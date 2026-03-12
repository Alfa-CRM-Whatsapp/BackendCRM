from core.crm.models import WhatsappMessage, ContactWhatsapp, WhatsappNumber
from rest_framework import serializers

class WhatsappMessageListSerializer(serializers.ModelSerializer):

    class Meta:
        model = WhatsappMessage
        fields = [
            'id',
            'type',
            'messaging_product',
            'contact',
            'messages',
            'from_number'
        ]

class WhatsappMessageCreateSerializer(serializers.Serializer):
    id_message = serializers.CharField(max_length=255)
    type = serializers.CharField(max_length=50)
    messaging_product = serializers.CharField(max_length=100)
    contact = serializers.PrimaryKeyRelatedField(queryset=ContactWhatsapp.objects.all())
    messages = serializers.JSONField()
    from_number = serializers.PrimaryKeyRelatedField(queryset=WhatsappNumber.objects.all())

