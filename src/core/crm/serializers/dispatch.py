from rest_framework import serializers

from core.crm.models import (
    ContactWhatsapp,
    Dispatch,
    WhatsAppTemplate,
    WhatsappNumber,
)
from .contact import ContactWhatsappListSerializer
from .templates import WhatsAppTemplateSerializer


class DispatchSerializer(serializers.ModelSerializer):
    contacts = ContactWhatsappListSerializer(many=True, read_only=True)
    template = WhatsAppTemplateSerializer(read_only=True)

    contact_ids = serializers.PrimaryKeyRelatedField(
        queryset=ContactWhatsapp.objects.all(),
        many=True,
        write_only=True,
        source="contacts"
    )
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=WhatsAppTemplate.objects.all(),
        write_only=True,
        source="template"
    )

    class Meta:
        model = Dispatch
        fields = [
            "id",
            "template",
            "template_id",
            "contacts",
            "contact_ids",
            "created_at",
            "executed_at",
        ]
        read_only_fields = ["id", "created_at", "executed_at", "template", "contacts"]


class DispatchExecuteSerializer(serializers.Serializer):
    from_number = serializers.PrimaryKeyRelatedField(
        queryset=WhatsappNumber.objects.all()
    )
    parameter_overrides = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        default=dict
    )
