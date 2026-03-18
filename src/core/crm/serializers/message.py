from core.crm.models import (
    WhatsappMessage,
    ContactWhatsapp,
    WhatsappNumber,
    OutboundWhatsappMessage,
    Chat
)
from rest_framework import serializers
from .contact import ContactWhatsappListSerializer
from .number import WhatsappNumberSerializer


# =========================
# INBOUND (recebidas)
# =========================
class WhatsappMessageListSerializer(serializers.ModelSerializer):

    contact = ContactWhatsappListSerializer(read_only=True)
    from_number = WhatsappNumberSerializer(read_only=True)
    chat_id = serializers.IntegerField(source='chat.id', read_only=True)

    class Meta:
        model = WhatsappMessage
        fields = [
            'id',
            'id_message',
            'type',
            'messaging_product',
            'contact',
            'messages',
            'from_number',
            'chat_id',
            'created_at',
        ]


class WhatsappMessageCreateSerializer(serializers.Serializer):
    id_message = serializers.CharField(max_length=255)
    type = serializers.CharField(max_length=50)
    messaging_product = serializers.CharField(max_length=100)

    contact = serializers.PrimaryKeyRelatedField(
        queryset=ContactWhatsapp.objects.all()
    )

    messages = serializers.JSONField()

    from_number = serializers.PrimaryKeyRelatedField(
        queryset=WhatsappNumber.objects.all()
    )

    def create(self, validated_data):
        contact = validated_data['contact']
        from_number = validated_data['from_number']

        chat, _ = Chat.objects.get_or_create(
            contact=contact,
            from_number=from_number
        )

        return WhatsappMessage.objects.create(
            id_message=validated_data['id_message'],
            type=validated_data['type'],
            messaging_product=validated_data['messaging_product'],
            contact=contact,
            from_number=from_number,
            chat=chat,
            messages=validated_data['messages'],
        )


# =========================
# OUTBOUND (enviadas)
# =========================
class OutboundWhatsappMessageListSerializer(serializers.ModelSerializer):

    contact_name = serializers.CharField(source='contact.profile_name', read_only=True)
    contact_number = serializers.CharField(source='contact.number', read_only=True)

    from_number_display = serializers.CharField(
        source='from_number.display_phone_number',
        read_only=True
    )

    chat_id = serializers.IntegerField(source='chat.id', read_only=True)

    class Meta:
        model = OutboundWhatsappMessage
        fields = [
            'id',
            'id_message',
            'message',
            'status',
            'contact',
            'contact_name',
            'contact_number',
            'from_number',
            'from_number_display',
            'chat_id',
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

    message = serializers.JSONField()

    def create(self, validated_data):
        contact = validated_data['contact']
        from_number = validated_data['from_number']

        # 🔥 mesma lógica aqui
        chat, _ = Chat.objects.get_or_create(
            contact=contact,
            from_number=from_number
        )

        return OutboundWhatsappMessage.objects.create(
            contact=contact,
            from_number=from_number,
            chat=chat,
            message=validated_data['message'],
            status="sent"
        )