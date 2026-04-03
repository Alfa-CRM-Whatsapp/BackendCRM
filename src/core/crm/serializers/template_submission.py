from rest_framework import serializers
from core.crm.models import TemplateSubmission

class TemplateSubmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplateSubmission
        fields = [
            "id",
            "template",
            "status",
            "response",
            "meta_template_id",
            "attempt",
            "created_at",
        ]

        read_only_fields = [
            "status",
            "response",
            "meta_template_id",
            "attempt",
            "created_at",
        ]