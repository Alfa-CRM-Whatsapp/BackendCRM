from rest_framework import serializers
from core.crm.models import (
    TemplateParameter,
    TemplateComponent,
    WhatsAppTemplate,
    TemplateButton,
    ContactWhatsapp,
    WhatsappNumber
)

class TemplateParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplateParameter
        fields = [
            "id",
            "name",
            "position",
            "param_type",
            "example_value",
            "order",
        ]

    def validate(self, data):
        name = data.get("name")
        position = data.get("position")

        if name and position:
            raise serializers.ValidationError("Use 'name' ou 'position', não ambos.")

        if not name and not position:
            raise serializers.ValidationError(
                "Informe 'name' (named) ou 'position' (positional)."
            )

        return data


class TemplateButtonSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplateButton
        fields = [
            "id",
            "type",
            "text",
            "url",
            "phone_number",
            "order",
        ]

    def validate(self, data):
        btn_type = data.get("type")

        if btn_type == "url" and not data.get("url"):
            raise serializers.ValidationError("Botão URL precisa de 'url'")

        if btn_type == "phone_number" and not data.get("phone_number"):
            raise serializers.ValidationError("Botão phone precisa de 'phone_number'")

        return data


class TemplateComponentSerializer(serializers.ModelSerializer):

    parameters = TemplateParameterSerializer(many=True, required=False)
    buttons = TemplateButtonSerializer(many=True, required=False)

    class Meta:
        model = TemplateComponent
        fields = [
            "id",
            "type",
            "text",
            "header_format",
            "example_media_url",
            "order",
            "parameters",
            "buttons",
        ]

    def validate(self, data):
        instance = getattr(self, "instance", None)

        component_type = data.get("type", getattr(instance, "type", None))
        header_format = data.get("header_format", getattr(instance, "header_format", None))
        text = data.get("text", getattr(instance, "text", None))
        example_media_url = data.get("example_media_url", getattr(instance, "example_media_url", None))

        if component_type == "header":
            # Default para manter compatibilidade quando format nao vier no payload.
            if not header_format:
                header_format = "text"
                data["header_format"] = "text"

            if header_format == "text" and not text:
                raise serializers.ValidationError(
                    "Para componente HEADER com format 'text', o campo 'text' e obrigatorio."
                )

            if header_format in ["image", "video", "document"] and not example_media_url:
                raise serializers.ValidationError(
                    "Para componente HEADER com format 'image/video/document', o campo 'example_media_url' e obrigatorio."
                )

        return data


class WhatsAppTemplateSerializer(serializers.ModelSerializer):

    components = TemplateComponentSerializer(many=True)

    class Meta:
        model = WhatsAppTemplate
        fields = [
            "id",
            "name",
            "meta_template_id",
            "language",
            "category",
            "parameter_format",
            "status",
            "quality_rating",
            "components",
        ]

class SendTemplateMessageSerializer(serializers.Serializer):
    contact = serializers.IntegerField()
    template = serializers.IntegerField()
    parameters = serializers.DictField(child=serializers.CharField(), required=False, default=dict)
    # Aceita id direto em from_number ou from_number_obj; tambem aceita objeto com id em from_number_obj.
    from_number = serializers.IntegerField(required=False, write_only=True)
    from_number_obj = serializers.JSONField(required=False, write_only=True)

    def validate(self, data):
        try:
            data["contact_obj"] = ContactWhatsapp.objects.get(id=data["contact"])
        except ContactWhatsapp.DoesNotExist:
            raise serializers.ValidationError("Contato não encontrado")

        try:
            data["template_obj"] = WhatsAppTemplate.objects.get(id=data["template"])
        except WhatsAppTemplate.DoesNotExist:
            raise serializers.ValidationError("Template não encontrado")

        raw_from_number = data.get("from_number_obj", data.get("from_number"))

        if raw_from_number is None:
            raise serializers.ValidationError(
                "from_number (ou from_number_obj) e obrigatorio"
            )

        if isinstance(raw_from_number, dict):
            from_number_id = raw_from_number.get("id")
        else:
            from_number_id = raw_from_number

        try:
            from_number_id = int(from_number_id)
        except (TypeError, ValueError):
            raise serializers.ValidationError("from_number deve ser um id inteiro valido")

        try:
            data["from_number_obj"] = WhatsappNumber.objects.get(id=from_number_id)
        except WhatsappNumber.DoesNotExist:
            raise serializers.ValidationError("Numero remetente nao encontrado")

        return data