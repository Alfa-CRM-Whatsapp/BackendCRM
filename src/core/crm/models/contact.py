from django.db import models 

class ContactWhatsapp(models.Model):
    phone_number_id = models.CharField(max_length=255)
    display_phone_number = models.CharField(max_length=255)
    profile_name = models.CharField(max_length=255)
    wa_id = models.CharField(max_length=255, unique=True)
    number = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.profile_name} - {self.display_phone_number}"