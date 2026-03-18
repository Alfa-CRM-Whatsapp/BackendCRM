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
    
class UserPreferences(models.Model):

    class ThemeChoices(models.TextChoices):
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'Dark'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences', null=False, blank=False)
    theme = models.CharField(max_length=10, choices=ThemeChoices.choices, default=ThemeChoices.LIGHT)
    primary_color = models.CharField(max_length=7, default='#1E3A5F')  

    def __str__(self):
        return f"Preferences for {self.user.email}"