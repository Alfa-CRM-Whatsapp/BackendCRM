from rest_framework import serializers
from core.crm.models import MessageCategory, CategoryExample


class CategoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryExample
        fields = [
            "id",
            "category",
            "text",
            "is_positive",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]

class MessageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageCategory
        fields = [
            "id",
            "name",
            "description",
            "color",
            "is_active",
            "whatsapp_number",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]