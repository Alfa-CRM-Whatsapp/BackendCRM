from rest_framework import serializers
from core.crm.models import (
    TemplateParameter,
    TemplateComponent,
    WhatsAppTemplate,
    TemplateButton,
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


class WhatsAppTemplateSerializer(serializers.ModelSerializer):

    components = TemplateComponentSerializer(many=True)

    class Meta:
        model = WhatsAppTemplate
        fields = [
            "id",
            "name",
            "language",
            "category",
            "parameter_format",
            "status",
            "quality_rating",
            "components",
        ]
