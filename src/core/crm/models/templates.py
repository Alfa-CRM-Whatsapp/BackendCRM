from django.db import models


class WhatsAppTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('utility', 'Utility'),
        ('marketing', 'Marketing'),
        ('authentication', 'Authentication'),
    ]

    LANGUAGE_CHOICES = [
        ('pt_BR', 'Portuguese (Brazil)'),
        ('en_US', 'English (United States)'),
    ]

    PARAM_FORMAT_CHOICES = [
        ('named', 'Named'),
        ('positional', 'Positional'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),            
        ('IN_REVIEW', 'In Review'),       
        ('APPROVED', 'Approved'),          
        ('REJECTED', 'Rejected'),          
        ('PAUSED', 'Paused'),              
        ('DISABLED', 'Disabled'),          
        ('APPEAL_REQUESTED', 'Appeal Requested'),
    ]

    QUALITY_CHOICES = [
        ('UNKNOWN', 'Unknown'),
        ('PENDING', 'Quality Pending'),
        ('HIGH', 'High Quality'),
        ('MEDIUM', 'Medium Quality'),
        ('LOW', 'Low Quality'),
    ]

    name = models.CharField(max_length=512)
    language = models.CharField(max_length=10, default='pt_BR', choices=LANGUAGE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    parameter_format = models.CharField(
        max_length=20,
        choices=PARAM_FORMAT_CHOICES,
        default='named'
    )

    meta_template_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    quality_rating = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        default='UNKNOWN'
    )

    rejection_reason = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    ttl_seconds = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.language})"

class TemplateComponent(models.Model):

    COMPONENT_TYPE_CHOICES = [
        ('header', 'Header'),
        ('body', 'Body'),
        ('footer', 'Footer'),
        ('buttons', 'Buttons'),
    ]

    HEADER_FORMAT_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]

    template = models.ForeignKey(
        WhatsAppTemplate,
        on_delete=models.CASCADE,
        related_name="components"
    )

    type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES)

    text = models.TextField(blank=True, null=True)

    header_format = models.CharField(
        max_length=20,
        choices=HEADER_FORMAT_CHOICES,
        blank=True,
        null=True
    )

    example_media_url = models.URLField(blank=True, null=True)

    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.template.name} - {self.type}"
    
from django.db import models


class TemplateParameter(models.Model):

    PARAM_TYPE_CHOICES = [
        ('text', 'Text'),
        ('currency', 'Currency'),
        ('date_time', 'Date Time'),
    ]

    component = models.ForeignKey(
        TemplateComponent,
        on_delete=models.CASCADE,
        related_name="parameters"
    )

    name = models.CharField(max_length=100, blank=True, null=True)

    position = models.IntegerField(blank=True, null=True)

    param_type = models.CharField(
        max_length=20,
        choices=PARAM_TYPE_CHOICES,
        default='text'
    )

    example_value = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Param {self.position}"
    
class TemplateButton(models.Model):
    BUTTON_TYPE_CHOICES = [
        ('quick_reply', 'Quick Reply'),
        ('url', 'URL'),
        ('phone_number', 'Phone Number'),
    ]

    component = models.ForeignKey(
        TemplateComponent,
        on_delete=models.CASCADE,
        related_name="buttons"
    )

    type = models.CharField(max_length=20, choices=BUTTON_TYPE_CHOICES)

    text = models.CharField(max_length=50)

    url = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    order = models.IntegerField(default=0)