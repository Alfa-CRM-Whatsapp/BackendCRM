from rest_framework import viewsets
from core.crm.models import Chat, WhatsappMessage, OutboundWhatsappMessage
from core.crm.serializers import ChatSerializer, ChatRetrieveSerializer, ChatCreateSerializer
from rest_framework.response import Response
from django.db.models import Q

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatRetrieveSerializer
        if self.action == 'create':
            return ChatCreateSerializer
        return ChatSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        category_param = request.query_params.get("category")

        inbound = (
            WhatsappMessage.objects
            .filter(chat=instance)
            .select_related('category')
        )

        if category_param:
            values = category_param.split(',')

            inbound = inbound.filter(
                Q(category__name__in=values) |
                Q(category__id__in=[v for v in values if v.isdigit()])
            )

        outbound = OutboundWhatsappMessage.objects.filter(chat=instance)

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
                "category": None,
                "category_confidence": None
            })

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