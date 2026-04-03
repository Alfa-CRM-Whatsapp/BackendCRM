from django.db import models


class TemplateSubmission(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]

    template = models.ForeignKey(
        "WhatsAppTemplate",
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    response = models.JSONField(null=True, blank=True)

    meta_template_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    attempt = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.template.name} - {self.status}"