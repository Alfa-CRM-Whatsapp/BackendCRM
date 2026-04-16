import uuid

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.crm.models import Chat, Dispatch, OutboundWhatsappMessage
from core.crm.serializers import DispatchExecuteSerializer, DispatchSerializer


class DispatchViewSet(viewsets.ModelViewSet):
    queryset = Dispatch.objects.all().prefetch_related(
        "contacts",
        "template__components__parameters",
        "template__components__buttons",
    )
    serializer_class = DispatchSerializer

    @staticmethod
    def _stringify_dict(data):
        return {str(key): str(value) for key, value in (data or {}).items()}

    @staticmethod
    def _resolve_parameter_value(parameter, global_overrides):
        keys = []

        if parameter.name:
            keys.append(str(parameter.name))

        if parameter.position is not None:
            keys.append(str(parameter.position))

        for key in keys:
            if key in global_overrides:
                return global_overrides[key]

        return parameter.example_value

    @staticmethod
    def _render_text_with_parameters(text, parameters_payload):
        if not text:
            return text

        rendered = text

        for param in parameters_payload:
            if param.get("name"):
                rendered = rendered.replace(
                    f"{{{{{param['name']}}}}}",
                    str(param.get("value", ""))
                )

        return rendered

    def _build_template_components_payload(self, template, global_overrides):
        components_payload = []

        for component in template.components.all().order_by("order"):
            parameters_payload = []
            for parameter in component.parameters.all().order_by("order"):
                resolved_value = self._resolve_parameter_value(
                    parameter,
                    global_overrides,
                )

                parameters_payload.append(
                    {
                        "id": parameter.id,
                        "name": parameter.name,
                        "position": parameter.position,
                        "param_type": parameter.param_type,
                        "value": resolved_value,
                    }
                )

            buttons_payload = []
            for button in component.buttons.all().order_by("order"):
                buttons_payload.append(
                    {
                        "id": button.id,
                        "type": button.type,
                        "text": button.text,
                        "url": button.url,
                        "phone_number": button.phone_number,
                        "order": button.order,
                    }
                )

            rendered_text = self._render_text_with_parameters(
                component.text,
                parameters_payload,
            )

            components_payload.append(
                {
                    "id": component.id,
                    "type": component.type,
                    "text": component.text,
                    "rendered_text": rendered_text,
                    "header_format": component.header_format,
                    "example_media_url": component.example_media_url,
                    "order": component.order,
                    "parameters": parameters_payload,
                    "buttons": buttons_payload,
                }
            )

        return components_payload

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        contacts = validated_data.pop("contacts", [])

        dispatch = Dispatch.objects.create(**validated_data)
        dispatch.contacts.set(contacts)

        output = self.get_serializer(dispatch)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        contacts = validated_data.pop("contacts", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if contacts is not None:
            instance.contacts.set(contacts)

        output = self.get_serializer(instance)
        return Response(output.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def execute(self, request, *args, **kwargs):
        dispatch = self.get_object()

        serializer = DispatchExecuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_number = serializer.validated_data["from_number"]
        global_overrides = self._stringify_dict(
            serializer.validated_data.get("parameter_overrides", {})
        )
        now = timezone.now()

        sent_count = 0

        for contact in dispatch.contacts.all():
            template_components = self._build_template_components_payload(
                dispatch.template,
                global_overrides,
            )

            chat, _ = Chat.objects.get_or_create(
                contact=contact,
                from_number=from_number
            )

            local_message_id = f"local-dispatch-{uuid.uuid4().hex}"

            message_json = {
                "id": local_message_id,
                "type": "template",
                "timestamp": str(int(now.timestamp())),
                "template": {
                    "id": dispatch.template.id,
                    "name": dispatch.template.name,
                    "language": dispatch.template.language,
                    "parameter_format": dispatch.template.parameter_format,
                    "components": template_components,
                },
                "mode": "local_dispatch",
                "dispatch_id": dispatch.id,
                "contact_id": contact.id,
            }

            OutboundWhatsappMessage.objects.create(
                id_message=local_message_id,
                contact=contact,
                from_number=from_number,
                chat=chat,
                message=message_json,
                status="sent",
                raw_response={
                    "mode": "local_dispatch",
                    "executed_at": now.isoformat(),
                }
            )

            sent_count += 1

        dispatch.executed_at = now
        dispatch.save(update_fields=["executed_at"])

        return Response(
            {
                "dispatch_id": dispatch.id,
                "template_id": dispatch.template_id,
                "sent_count": sent_count,
                "executed_at": dispatch.executed_at,
            },
            status=status.HTTP_200_OK,
        )