from django.db import models
from core.crm.models import ContactWhatsapp, WhatsappNumber
from .chat import Chat
from .category import MessageCategory

class WhatsappMessage(models.Model):
    id_message = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=50)
    messaging_product = models.CharField(max_length=100)

    contact = models.ForeignKey(
        ContactWhatsapp,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    from_number = models.ForeignKey(
        WhatsappNumber,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='inbound_messages',
        null=True,
        blank=True
    )

    messages = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(
        MessageCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages'
    )
    category_confidence = models.FloatField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'Message {self.id_message} for Contact {self.contact.id}'


class OutboundWhatsappMessage(models.Model):

    STATUS_CHOICES = [
        ("sent", "Enviado"),
        ("delivered", "Entregue"),
        ("read", "Lido"),
        ("failed", "Falhou"),
    ]

    id_message = models.CharField(max_length=255, unique=True)

    contact = models.ForeignKey(
        ContactWhatsapp,
        on_delete=models.CASCADE,
        related_name='outbound_messages'
    )

    from_number = models.ForeignKey(
        WhatsappNumber,
        on_delete=models.CASCADE,
        related_name='outbound_messages'
    )

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='outbound_messages',
        null=True,
        blank=True
    )

    message = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="sent"
    )

    raw_response = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Outbound {self.id_message} - {self.status}'