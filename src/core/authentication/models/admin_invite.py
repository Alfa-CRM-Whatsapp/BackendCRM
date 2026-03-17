import secrets
from django.conf import settings
from django.db import models

def generate_invite_code():
    return str(secrets.randbelow(900000) + 100000)
class SuperAdminInvite(models.Model):
    token = models.CharField(
        max_length=6,
        unique=True,
        editable=False
    )
    email = models.EmailField()
    password = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if not self.token:
            while True:
                code = generate_invite_code()
                if not SuperAdminInvite.objects.filter(token=code).exists():
                    self.token = code
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invite {self.email} - {self.token}"