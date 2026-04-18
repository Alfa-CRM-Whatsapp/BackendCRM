# ChatWindowValidationView

- Route: /api/chat-window-validation/
- View: ChatWindowValidationView

## Codigo Da View

Fonte: src\core\crm\views\chat_window.py

```python
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.crm.models import Chat, WhatsappMessage


class ChatWindowValidationView(APIView):
    def post(self, request):
        chat_id = request.data.get("chat_id") or request.query_params.get("chat_id")

        if not chat_id:
            return Response(
                {"error": "chat_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            chat_id = int(chat_id)
        except (TypeError, ValueError):
            return Response(
                {"error": "chat_id deve ser um inteiro"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response(
                {"error": "Chat não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        last_inbound_message = (
            WhatsappMessage.objects
            .filter(chat_id=chat_id)
            .order_by("-created_at")
            .first()
        )

        if not last_inbound_message:
            return Response(
                {
                    "chat_id": chat_id,
                    "window_open": False,
                    "reason": "Nenhuma mensagem recebida encontrada para este chat.",
                    "guidance": "Janela fechada: para iniciar conversa, envie template aprovado pela Meta.",
                },
                status=status.HTTP_200_OK,
            )

        now = timezone.now()
        expires_at = last_inbound_message.created_at + timedelta(hours=24)
        window_open = now <= expires_at

        remaining_seconds = max(0, int((expires_at - now).total_seconds()))

        return Response(
            {
                "chat_id": chat_id,
                "last_inbound_message_at": last_inbound_message.created_at,
                "window_expires_at": expires_at,
                "window_open": window_open,
                "remaining_seconds": remaining_seconds,
                "guidance": (
                    "Janela aberta: conversa pode continuar normalmente."
                    if window_open
                    else "Janela fechada: para iniciar conversa, envie template aprovado pela Meta."
                ),
            },
            status=status.HTTP_200_OK,
        )

```
