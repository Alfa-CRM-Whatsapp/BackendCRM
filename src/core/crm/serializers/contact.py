from rest_framework import serializers
from core.crm.models import ContactWhatsapp

class ContactWhatsappListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactWhatsapp
        fields = [
            'id', 
            'phone_number_id',
            'display_phone_number',
            'profile_name',
            'wa_id',
            'number'
        ]