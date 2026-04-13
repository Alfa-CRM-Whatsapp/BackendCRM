from rest_framework.viewsets import ModelViewSet

from core.crm.models import MessageCategory, CategoryExample
from core.crm.serializers.category import (
    MessageCategorySerializer,
    CategoryExampleSerializer
)


class MessageCategoryViewSet(ModelViewSet):
    queryset = MessageCategory.objects.all()
    serializer_class = MessageCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        whatsapp_number = self.request.query_params.get("whatsapp_number")

        if whatsapp_number:
            queryset = queryset.filter(whatsapp_number_id=whatsapp_number)

        return queryset


class CategoryExampleViewSet(ModelViewSet):
    queryset = CategoryExample.objects.all()
    serializer_class = CategoryExampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.query_params.get("category")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset