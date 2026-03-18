from rest_framework import viewsets
from core.crm.models import Chat, WhatsappMessage, OutboundWhatsappMessage
from core.crm.serializers import ChatSerializer, ChatRetrieveSerializer
from rest_framework.response import Response

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatRetrieveSerializer
        return ChatSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        inbound = WhatsappMessage.objects.filter(chat=instance)
        outbound = OutboundWhatsappMessage.objects.filter(chat=instance)

        messages = []

        for msg in inbound:
            messages.append({
                "id": msg.id,
                "type": msg.type,
                "direction": "inbound",
                "content": msg.messages,
                "created_at": msg.created_at
            })

        for msg in outbound:
            messages.append({
                "id": msg.id,
                "type": msg.message.get("type"),
                "direction": "outbound",
                "content": msg.message,
                "status": msg.status,
                "created_at": msg.created_at
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