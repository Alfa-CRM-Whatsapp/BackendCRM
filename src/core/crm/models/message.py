from django.db import models
from core.crm.models import ContactWhatsapp

class WhatsappMessage(models.Model):
    id_message = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=50)
    messaging_product = models.CharField(max_length=100)
    contact = models.ForeignKey(ContactWhatsapp, on_delete=models.CASCADE, related_name='messages')
    messages = models.JSONField()
    from_number = models.CharField(max_length=20)

    def __str__(self):
        return f'Message {self.message_id} for Contact {self.contact.id}'