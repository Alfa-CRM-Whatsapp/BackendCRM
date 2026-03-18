from rest_framework import serializers
from core.crm.models import WhatsappNumber

class WhatsappNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = WhatsappNumber
        fields = [
            'id',
            'display_phone_number',
            'phone_number_id',
            'name',
            'verified',
        ]