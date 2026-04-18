# MetricsView

- Route: /api/metrics/<str:metric_type>/
- View: MetricsView

## Codigo Da View

Fonte: src\core\crm\views\metrics.py

```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.crm.utils.metrics import (
    get_categories_metrics_cards,
    get_messages_metrics_cards,
    get_numbers_metrics_cards,
)


class MetricsView(APIView):
    METRIC_HANDLERS = {
        "categories": get_categories_metrics_cards,
        "numbers": get_numbers_metrics_cards,
        "messages": get_messages_metrics_cards,
    }

    def get(self, request, metric_type):
        handler = self.METRIC_HANDLERS.get((metric_type or "").lower())

        if not handler:
            return Response(
                {
                    "detail": "Tipo de metrica invalido. Use: categories, numbers ou messages.",
                    "available": list(self.METRIC_HANDLERS.keys()),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "metric": metric_type.lower(),
                "cards": handler(),
            }
        )

```

## Metodos Aceitos

### GET
- Consulta De Metricas: `GET /api/metrics/{metric_type}/`
- Parametro De Rota:
- `metric_type`: `categories`, `numbers` ou `messages`.
- Exemplo:
`GET /api/metrics/messages/`

