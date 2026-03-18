from rest_framework import serializers
from core.crm.models import Chat
from .contact import ContactWhatsappListSerializer
from .number import WhatsappNumberSerializer

class ChatSerializer(serializers.ModelSerializer):
    contact = ContactWhatsappListSerializer(read_only=True)
    from_number = WhatsappNumberSerializer(read_only=True)
    
    class Meta:
        model = Chat
        fields = [
            'id',
            'contact',
            'from_number',
        ]
        
class ChatRetrieveSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    contact = ContactWhatsappListSerializer(read_only=True)
    from_number = WhatsappNumberSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = [
            'id',
            'contact',
            'from_number',
            'messages',
        ]

    def get_messages(self, obj):
        return self.context.get("messages", [])