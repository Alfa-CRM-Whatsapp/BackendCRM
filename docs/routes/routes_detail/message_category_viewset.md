# MessageCategoryViewSet

- Route: /api/message-categories/
- View: MessageCategoryViewSet

## Codigo Da View

Fonte: src\core\crm\views\category.py

```python
from rest_framework.viewsets import ModelViewSet

from core.crm.models import MessageCategory, CategoryExample
from core.crm.serializers.category import (
    MessageCategorySerializer,
    CategoryExampleSerializer,
    CategoryExampleCreateSerializer
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

    def get_serializer_class(self):
        if self.action == "create":
            return CategoryExampleCreateSerializer
        return CategoryExampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.query_params.get("category")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[^/.]+)')
    def get_examples_by_category(self, request, category_id=None):
        """
        Retorna todos os exemplos de uma categoria específica
        Rota: /api/category-examples/by-category/{category_id}/
        """
        try:
            category_exists = MessageCategory.objects.filter(id=category_id).exists()
            
            if not category_exists:
                return Response(
                    {"error": f"Categoria com id {category_id} não encontrada"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            examples = CategoryExample.objects.filter(category_id=category_id)
            
            positive_examples = examples.filter(is_positive=True)
            negative_examples = examples.filter(is_positive=False)
            
            serializer = self.get_serializer(examples, many=True)
            
            category = MessageCategory.objects.get(id=category_id)
            category_serializer = MessageCategorySerializer(category)

            return Response({
                "category": category_serializer.data,
                "total_count": examples.count(),
                "positive_count": positive_examples.count(),
                "negative_count": negative_examples.count(),
                "examples": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


```

## Metodos Aceitos

### GET
- Lista: `GET /api/message-categories/`
- Detalhe: `GET /api/message-categories/{id}/`
- Query Params:
- `whatsapp_number`: Filtra por numero.
- Rota Extra:
- `GET /api/message-categories/by-number/{number_id}/all/`

### POST
- Criacao: `POST /api/message-categories/`
- Payload:
```json
{
  "whatsapp_number": 1,
  "name": "Suporte",
  "description": "Mensagens de suporte",
  "color": "#6c757d",
  "is_active": true
}
```

### PUT
- Atualizacao Completa: `PUT /api/message-categories/{id}/`

### PATCH
- Atualizacao Parcial: `PATCH /api/message-categories/{id}/`

### DELETE
- Remocao: `DELETE /api/message-categories/{id}/`

