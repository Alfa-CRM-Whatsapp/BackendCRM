from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction

from core.crm.models import WhatsAppTemplate, TemplateComponent, TemplateParameter, TemplateButton
from core.crm.serializers import WhatsAppTemplateSerializer, TemplateComponentSerializer, TemplateParameterSerializer, TemplateButtonSerializer


class WhatsAppTemplateViewSet(viewsets.ModelViewSet):
    queryset = WhatsAppTemplate.objects.all()
    serializer_class = WhatsAppTemplateSerializer

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
