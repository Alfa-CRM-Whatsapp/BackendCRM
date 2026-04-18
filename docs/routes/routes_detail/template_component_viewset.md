# TemplateComponentViewSet

- Route: /api/template-components/
- View: TemplateComponentViewSet

## Codigo Da View

Fonte: src\core\crm\views\templates.py

```python
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from rest_framework.exceptions import ValidationError   

from core.crm.models import WhatsAppTemplate, TemplateComponent, TemplateParameter, TemplateButton
from core.crm.serializers import WhatsAppTemplateSerializer, TemplateComponentSerializer, TemplateParameterSerializer, TemplateButtonSerializer
from django.conf import settings


class WhatsAppTemplateViewSet(viewsets.ModelViewSet):
    queryset = WhatsAppTemplate.objects.all()
    serializer_class = WhatsAppTemplateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.meta_template_id:
            try:
                url = f"https://graph.facebook.com/v23.0/{settings.BM_ID}/message_templates"
                params = {
                    "name": instance.name,
                    "language": instance.language
                }
                headers = {
                    "Authorization": f"Bearer {settings.ACCESS_TOKEN}",
                }
                response = requests.delete(url, headers=headers, params=params, timeout=30)
            except Exception as e:
                raise ValidationError(f"Erro ao tentar deletar template no Meta: {str(e)}")

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        with transaction.atomic():

            template = WhatsAppTemplate.objects.create(
                name=data["name"],
                language=data["language"],
                category=data["category"],
                parameter_format=data["parameter_format"],
            )

            for comp_data in data["components"]:
                parameters_data = comp_data.pop("parameters", [])
                buttons_data = comp_data.pop("buttons", [])

                component = TemplateComponent.objects.create(
                    template=template,
                    **comp_data
                )

                for param_data in parameters_data:
                    TemplateParameter.objects.create(
                        component=component,
                        **param_data
                    )

                for btn_data in buttons_data:
                    TemplateButton.objects.create(
                        component=component,
                        **btn_data
                    )

        return Response({"id": template.id}, status=201)
    
class TemplateComponentViewSet(viewsets.ModelViewSet):
    queryset = TemplateComponent.objects.all()
    serializer_class = TemplateComponentSerializer

class TemplateParameterViewSet(viewsets.ModelViewSet):
    queryset = TemplateParameter.objects.all()
    serializer_class = TemplateParameterSerializer

class TemplateButtonViewSet(viewsets.ModelViewSet):
    queryset = TemplateButton.objects.all()
    serializer_class = TemplateButtonSerializer

```
