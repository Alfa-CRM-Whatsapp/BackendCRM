from rest_framework import viewsets
from rest_framework.response import Response
import requests

from core.crm.models import TemplateSubmission, WhatsAppTemplate
from core.crm.serializers import TemplateSubmissionSerializer
from django.conf import settings


class TemplateSubmissionViewSet(viewsets.ModelViewSet):
    queryset = TemplateSubmission.objects.all()
    serializer_class = TemplateSubmissionSerializer

    def build_body_examples(self, component, template):
        params = component.parameters.all().order_by("order")

        if template.parameter_format == "named":
            return {
                "body_text_named_params": [
                    {
                        "param_name": p.name,
                        "example": p.example_value
                    }
                    for p in params
                ]
            }
        else:
            return {
                "body_text": [
                    [p.example_value for p in params]
                ]
            }

    def build_components_for_meta(self, template):
        components = []

        for comp in template.components.all().order_by("order"):
            component_type = (comp.type or "").lower()

            if component_type not in ["header", "body", "footer", "buttons"]:
                raise ValueError(
                    f"Tipo de componente invalido para Meta: '{comp.type}'."
                )

            comp_data = {
                "type": component_type
            }

            if component_type == "header":
                # Compatibilidade com templates antigos sem format salvo.
                header_format = (comp.header_format or "text").lower()
                comp_data["format"] = header_format

                if header_format == "text":
                    if not comp.text:
                        raise ValueError(
                            "Componente HEADER com format 'text' exige o campo 'text'."
                        )

                    comp_data["text"] = comp.text

                    if comp.parameters.exists():
                        if template.parameter_format == "named":
                            comp_data["example"] = {
                                "header_text_named_params": [
                                    {
                                        "param_name": p.name,
                                        "example": p.example_value
                                    }
                                    for p in comp.parameters.all().order_by("order")
                                ]
                            }
                        else:
                            comp_data["example"] = {
                                "header_text": [
                                    [p.example_value for p in comp.parameters.all().order_by("order")]
                                ]
                            }

                elif header_format in ["image", "video", "document"]:
                    if not comp.example_media_url:
                        raise ValueError(
                            "Componente HEADER com format 'image/video/document' exige 'example_media_url'."
                        )

                    comp_data["example"] = {
                        "header_handle": [comp.example_media_url]
                    }

            elif component_type == "body":
                comp_data["text"] = comp.text

                if comp.parameters.exists():
                    comp_data["example"] = self.build_body_examples(comp, template)

            elif component_type == "footer":
                comp_data["text"] = comp.text

            elif component_type == "buttons":
                comp_data["buttons"] = []

                for btn in comp.buttons.all().order_by("order"):
                    button_type = (btn.type or "").lower()
                    btn_data = {
                        "type": button_type,
                        "text": btn.text
                    }

                    if button_type == "url":
                        btn_data["url"] = btn.url

                    if button_type == "phone_number":
                        btn_data["phone_number"] = btn.phone_number

                    comp_data["buttons"].append(btn_data)

            components.append(comp_data)

        return components

    def create(self, request, *args, **kwargs):
        template_id = request.data.get("template")

        if not template_id:
            return Response(
                {"error": "template é obrigatório"},
                status=400
            )

        try:
            template = WhatsAppTemplate.objects.get(id=template_id)
        except WhatsAppTemplate.DoesNotExist:
            return Response(
                {"error": "Template não encontrado"},
                status=404
            )

        last_attempt = template.submissions.count() + 1

        submission = TemplateSubmission.objects.create(
            template=template,
            attempt=last_attempt
        )

        try:
            components = self.build_components_for_meta(template)
        except ValueError as exc:
            return Response(
                {
                    "error": str(exc),
                    "detail": "Corrija o template antes de submeter para a Meta.",
                },
                status=400,
            )

        payload = {
            "name": template.name,
            "language": template.language,
            "category": template.category,
            "parameter_format": template.parameter_format,
            "components": components
        }

        url = f"https://graph.facebook.com/v23.0/{settings.BM_ID}/message_templates"

        headers = {
            "Authorization": f"Bearer {settings.ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200:
            submission.status = "success"
            submission.meta_template_id = data.get("id")
            submission.response = data

            template.meta_template_id = data.get("id")
            template.status = "IN_REVIEW"
            template.save()

        else:
            submission.status = "error"
            submission.response = data

        submission.save()

        return Response({
            "submission_id": submission.id,
            "status": submission.status,
            "meta_response": data
        }, status=201)