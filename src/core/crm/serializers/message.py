from core.crm.models import WhatsappMessage, ContactWhatsapp, WhatsappNumber, OutboundWhatsappMessage
from rest_framework import serializers
from .contact import ContactWhatsappListSerializer
from .number import WhatsappNumberSerializer

class WhatsappMessageListSerializer(serializers.ModelSerializer):

    contact = ContactWhatsappListSerializer(read_only=True)
    from_number = WhatsappNumberSerializer(read_only=True)

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

class OutboundWhatsappMessageListSerializer(serializers.ModelSerializer):

    contact_name = serializers.CharField(source='contact.profile_name', read_only=True)
    contact_number = serializers.CharField(source='contact.number', read_only=True)

    from_number_display = serializers.CharField(source='from_number.display_phone_number', read_only=True)

    class Meta:
        model = OutboundWhatsappMessage
        fields = [
            'id',
            'id_message',
            'message_text',
            'status',
            'contact',
            'contact_name',
            'contact_number',
            'from_number',
            'from_number_display',
            'created_at',
            'updated_at',
        ]


class OutboundWhatsappMessageCreateSerializer(serializers.Serializer):

    contact = serializers.PrimaryKeyRelatedField(
        queryset=ContactWhatsapp.objects.all()
    )

    from_number = serializers.PrimaryKeyRelatedField(
        queryset=WhatsappNumber.objects.all()
    )

    message_text = serializers.CharField()

    def create(self, validated_data):
        # ⚠️ id_message e status serão definidos depois da resposta da API
        return OutboundWhatsappMessage.objects.create(
            contact=validated_data['contact'],
            from_number=validated_data['from_number'],
            message_text=validated_data['message_text'],
            status="sent"
        )