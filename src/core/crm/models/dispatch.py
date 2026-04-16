from django.db import models


class Dispatch(models.Model):
    template = models.ForeignKey(
        "WhatsAppTemplate",
        on_delete=models.CASCADE,
        related_name="dispatches"
    )
    contacts = models.ManyToManyField(
        "ContactWhatsapp",
        related_name="dispatches"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Dispatch {self.id} - {self.template.name}"