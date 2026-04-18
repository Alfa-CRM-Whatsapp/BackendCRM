# MyChatsViewSet (list)

- Route: /api/my-chats/
- View: MyChatsViewSet (list)

## Codigo Da View

Fonte: src\core\crm\views\chat.py

```python
from rest_framework import viewsets
from core.crm.models import Chat, WhatsappMessage, OutboundWhatsappMessage
from core.crm.serializers import ChatSerializer, ChatRetrieveSerializer, ChatCreateSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()

    @staticmethod
    def _parse_int_param(value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_message_text(content):
        """Extrai texto pesquisavel quando a mensagem possui campos textuais."""
        if content is None:
            return ""

        if isinstance(content, str):
            return content

        if not isinstance(content, (dict, list)):
            return ""

        collected = []
        textual_keys = {
            "body",
            "text",
            "caption",
            "title",
            "description",
            "name",
        }

        def walk(value):
            if isinstance(value, str):
                collected.append(value)
                return

            if isinstance(value, list):
                for item in value:
                    walk(item)
                return

            if isinstance(value, dict):
                for key, nested in value.items():
                    if isinstance(nested, str) and str(key).lower() in textual_keys:
                        collected.append(nested)
                    elif isinstance(nested, (dict, list)):
                        walk(nested)

        walk(content)
        return " ".join(collected)

    @staticmethod
    def _normalize_search_param(value):
        term = (value or "").strip()
        if len(term) >= 2 and term[0] == term[-1] and term[0] in {'"', "'"}:
            return term[1:-1].strip()
        return term

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatRetrieveSerializer
        if self.action == 'create':
            return ChatCreateSerializer
        return ChatSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        category_param = request.query_params.get("category")
        direction_param = request.query_params.get("direction")
        raw_search_param = (
            request.query_params.get("search")
            or request.query_params.get("text")
            or request.query_params.get("q")
        )
        search_param = self._normalize_search_param(raw_search_param)
        year = self._parse_int_param(request.query_params.get("year"))
        month = self._parse_int_param(request.query_params.get("month"))
        day = self._parse_int_param(request.query_params.get("day"))

        allowed_directions = {"inbound", "outbound"}
        selected_directions = {
            value.strip().lower()
            for value in (direction_param or "").split(",")
            if value.strip().lower() in allowed_directions
        }
        include_inbound = not selected_directions or "inbound" in selected_directions
        include_outbound = not selected_directions or "outbound" in selected_directions

        inbound = WhatsappMessage.objects.none()
        if include_inbound:
            inbound = (
                WhatsappMessage.objects
                .filter(chat=instance)
                .select_related('category')
            )

        if category_param and include_inbound:
            values = category_param.split(',')

            inbound = inbound.filter(
                Q(category__name__in=values) |
                Q(category__id__in=[v for v in values if v.isdigit()])
            )

        if year is not None and include_inbound:
            inbound = inbound.filter(created_at__year=year)
        if month is not None and include_inbound:
            inbound = inbound.filter(created_at__month=month)
        if day is not None and include_inbound:
            inbound = inbound.filter(created_at__day=day)

        outbound = OutboundWhatsappMessage.objects.none()
        if include_outbound:
            outbound = OutboundWhatsappMessage.objects.filter(chat=instance)

        if year is not None and include_outbound:
            outbound = outbound.filter(created_at__year=year)
        if month is not None and include_outbound:
            outbound = outbound.filter(created_at__month=month)
        if day is not None and include_outbound:
            outbound = outbound.filter(created_at__day=day)

        messages = []

        for msg in inbound:
            category_data = None

            if msg.category:
                category_data = {
                    "id": msg.category.id,
                    "name": msg.category.name,
                    "description": msg.category.description,
                    "color": msg.category.color,
                    "is_active": msg.category.is_active
                }

            messages.append({
                "id": msg.id,
                "type": msg.type,
                "direction": "inbound",
                "content": msg.messages,
                "created_at": msg.created_at,
                "category": category_data,
                "category_confidence": msg.category_confidence
            })

        for msg in outbound:
            messages.append({
                "id": msg.id,
                "type": msg.message.get("type"),
                "direction": "outbound",
                "content": msg.message,
                "status": msg.status,
                "created_at": msg.created_at,
                "with_template": msg.with_template,
                "category": None,
                "category_confidence": None
            })

        if search_param:
            query = search_param.lower()
            messages = [
                msg for msg in messages
                if query in self._extract_message_text(msg.get("content")).lower()
            ]

        messages.sort(key=lambda x: x["created_at"])

        serializer = self.get_serializer(
            instance,
            context={"messages": messages}
        )

        return Response(serializer.data)
    
class MyChatsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatSerializer

    def get_queryset(self):
        number_id = self.request.query_params.get("number_id")

        queryset = Chat.objects.all()

        if number_id:
            queryset = queryset.filter(from_number_id=number_id)

        return queryset.order_by("-id")

    @action(detail=False, methods=['get'], url_path='by-contact/(?P<contact_id>[^/.]+)')
    def by_contact(self, request, contact_id=None):
        queryset = self.get_queryset().filter(contact_id=contact_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```
