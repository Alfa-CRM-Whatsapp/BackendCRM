from django.contrib.auth.models import AbstractUser
from django.db import models
from core.authentication.managers import UserManager


class User(AbstractUser):

    username = models.CharField(max_length=150, blank=True, null=True)

    email = models.EmailField(unique=True)

    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email