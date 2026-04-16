from rest_framework import serializers
from core.crm.models import ContactWhatsapp

class ContactWhatsappListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = ContactWhatsapp
        fields = [
            'id', 
            'profile_name',
            'wa_id',
            'number',
            'created_at',
        ]