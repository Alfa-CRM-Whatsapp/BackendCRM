from django.db import models

class WhatsappNumber(models.Model):
    LANGUAGE_CHOICES = [
        ("pt_BR", "Portuguese (Brazil)"),
        ("en_US", "English (United States)"),
    ]

    display_phone_number = models.CharField(max_length=255)
    phone_number_id = models.CharField(max_length=255, unique=True)
    waba_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="pt_BR")
    pin = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=50, default="PENDING")
    account_event = models.CharField(max_length=100, blank=True, null=True)
    account_country = models.CharField(max_length=10, blank=True, null=True)
    account_violation_type = models.CharField(max_length=100, blank=True, null=True)
    account_ban_state = models.CharField(max_length=50, blank=True, null=True)
    account_ban_date = models.CharField(max_length=100, blank=True, null=True)
    account_ad_account_id = models.CharField(max_length=255, blank=True, null=True)
    account_owner_business_id = models.CharField(max_length=255, blank=True, null=True)
    auth_international_rate_eligibility = models.JSONField(default=dict, blank=True)
    volume_tier_info = models.JSONField(default=dict, blank=True)
    account_update_payload = models.JSONField(default=dict, blank=True)
    account_updated_at = models.DateTimeField(blank=True, null=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.display_phone_number}"