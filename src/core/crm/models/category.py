from django.db import models
from core.crm.models import WhatsappNumber
from core.authentication.models import User


class MessageCategory(models.Model):
    whatsapp_number = models.ForeignKey(
        WhatsappNumber,
        on_delete=models.CASCADE,
        related_name='message_categories'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True,
    )
    color = models.CharField(
        max_length=7,
        default="#6c757d",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_message_categories'
    )

    class Meta:
        unique_together = ('whatsapp_number', 'name')
        verbose_name = "Message Category"
        verbose_name_plural = "Message Categories"
        ordering = ['name']

    def __str__(self):
        return f"{self.whatsapp_number.name} - {self.name}"

class CategoryExample(models.Model):
    category = models.ForeignKey(
        MessageCategory,
        on_delete=models.CASCADE,
        related_name='examples'
    )
    text = models.TextField()
    is_positive = models.BooleanField(
        default=True,
    )

    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_category_examples'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Exemplo para "{self.category.name}": {self.text[:50]}...'