from django.db import models
from core.crm.models import ContactWhatsapp, WhatsappNumber

class Chat(models.Model):
    contact = models.ForeignKey(ContactWhatsapp, on_delete=models.CASCADE, related_name="chats")
    from_number = models.ForeignKey(WhatsappNumber, on_delete=models.CASCADE, related_name="chats")

    class Meta:
        unique_together = ("contact", "from_number")

    def __str__(self):
        return f"Chat with {self.contact} from {self.from_number}"