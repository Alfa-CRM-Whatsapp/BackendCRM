from django.db import models

class WhatsappNumber(models.Model):
    display_phone_number = models.CharField(max_length=255)
    phone_number_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.display_phone_number}"