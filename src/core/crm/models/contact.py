from django.db import models 
from rest_framework import serializers
import re

def normalize_phone(number: str) -> str:
    if not number:
        return number

    number = re.sub(r'\D', '', number)

    if number.startswith("55") and len(number) >= 12:
        return number

    if len(number) == 11:
        return "55" + number

    if len(number) in [8, 9]:
        raise serializers.ValidationError("Número sem DDD não é permitido")

    return number

class ContactWhatsapp(models.Model):
    profile_name = models.CharField(max_length=255)
    wa_id = models.CharField(max_length=255, unique=True)
    number = models.CharField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.wa_id = normalize_phone(self.wa_id)
        self.number = normalize_phone(self.number)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profile_name} - {self.number}"