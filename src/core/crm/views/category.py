from rest_framework.viewsets import ModelViewSet

from core.crm.models import MessageCategory, CategoryExample
from core.crm.serializers.category import (
    MessageCategorySerializer,
    CategoryExampleSerializer
)

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

class MessageCategoryViewSet(ModelViewSet):
    queryset = MessageCategory.objects.all()
    serializer_class = MessageCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        whatsapp_number = self.request.query_params.get("whatsapp_number")

        if whatsapp_number:
            queryset = queryset.filter(whatsapp_number_id=whatsapp_number)

        return queryset

    @action(detail=False, methods=['get'], url_path='by-number/(?P<number_id>[^/.]+)/all')
    def get_all_categories_by_number(self, request, number_id=None):
        try:
            categories = MessageCategory.objects.filter(
                whatsapp_number_id=number_id
            )
            serializer = self.get_serializer(categories, many=True)
            return Response({
                "number_id": number_id,
                "count": categories.count(),
                "active_count": categories.filter(is_active=True).count(),
                "inactive_count": categories.filter(is_active=False).count(),
                "categories": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryExampleViewSet(ModelViewSet):
    queryset = CategoryExample.objects.all()
    serializer_class = CategoryExampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.query_params.get("category")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset