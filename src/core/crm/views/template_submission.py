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

            comp_data = {
                "type": comp.type
            }

            if comp.type == "header":
                comp_data["format"] = comp.header_format

                if comp.header_format == "text":
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

                elif comp.header_format in ["image", "video", "document"]:
                    comp_data["example"] = {
                        "header_handle": [comp.example_media_url]
                    }

            elif comp.type == "body":
                comp_data["text"] = comp.text

                if comp.parameters.exists():
                    comp_data["example"] = self.build_body_examples(comp, template)

            elif comp.type == "footer":
                comp_data["text"] = comp.text

            elif comp.type == "buttons":
                comp_data["buttons"] = []

                for btn in comp.buttons.all().order_by("order"):
                    btn_data = {
                        "type": btn.type,
                        "text": btn.text
                    }

                    if btn.type == "url":
                        btn_data["url"] = btn.url

                    if btn.type == "phone_number":
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

        components = self.build_components_for_meta(template)

        payload = {
            "name": template.name,
            "language": template.language,
            "category": template.category,
            "parameter_format": template.parameter_format,
            "components": components
        }

        url = f"https://graph.facebook.com/v23.0/{settings.WABA_ID}/message_templates"

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