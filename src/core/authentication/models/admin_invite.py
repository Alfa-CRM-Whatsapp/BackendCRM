import uuid
from django.conf import settings
from django.db import models


class SuperAdminInvite(models.Model):

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

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

    def __str__(self):
        return f"Invite {self.email}"