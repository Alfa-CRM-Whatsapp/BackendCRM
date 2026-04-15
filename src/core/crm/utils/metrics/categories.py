from django.db.models import Count

from core.crm.models import CategoryExample, MessageCategory, WhatsappMessage


def _build_number_label(number_name):
    return number_name or "Sem numero"


def _get_top_category_by_examples():
    top = (
        CategoryExample.objects
        .values(
            "category_id",
            "category__name",
            "category__whatsapp_number__name",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "category__name")
        .first()
    )

    if not top:
        return None

    return {
        "categoryName": top["category__name"],
        "numberLabel": _build_number_label(top["category__whatsapp_number__name"]),
        "count": top["count"],
    }


def _get_top_category_by_messages():
    top = (
        WhatsappMessage.objects
        .filter(category__isnull=False)
        .values(
            "category_id",
            "category__name",
            "category__whatsapp_number__name",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "category__name")
        .first()
    )

    if not top:
        return None

    return {
        "categoryName": top["category__name"],
        "numberLabel": _build_number_label(top["category__whatsapp_number__name"]),
        "count": top["count"],
    }


def get_categories_metrics_cards():
    total_categories = MessageCategory.objects.count()
    total_examples = CategoryExample.objects.count()

    top_examples = _get_top_category_by_examples()
    top_messages = _get_top_category_by_messages()

    return [
        {
            "title": "Categorias Gerais",
            "value": total_categories,
            "icon": "mdi-tag-multiple",
            "color": "primary",
        },
        {
            "title": "Exemplos Gerais",
            "value": total_examples,
            "icon": "mdi-text-box-multiple",
            "color": "info",
        },
        {
            "title": "Categoria com Mais Exemplos",
            "value": (
                f"{top_examples['categoryName']} • {top_examples['numberLabel']} ({top_examples['count']})"
                if top_examples
                else "-"
            ),
            "icon": "mdi-trophy-outline",
            "color": "success",
        },
        {
            "title": "Categoria com Mais Mensagens",
            "value": (
                f"{top_messages['categoryName']} • {top_messages['numberLabel']} ({top_messages['count']})"
                if top_messages
                else "-"
            ),
            "icon": "mdi-message-badge-outline",
            "color": "warning",
        },
    ]
