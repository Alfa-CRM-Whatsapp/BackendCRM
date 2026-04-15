from django.db.models import Count

from core.crm.models import WhatsappMessage


def _build_number_label(name):
    return name or "Sem numero"


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


def _get_number_with_most_inbound():
    top = (
        WhatsappMessage.objects
        .values("from_number_id", "from_number__name")
        .annotate(count=Count("id"))
        .order_by("-count", "from_number__name")
        .first()
    )

    if not top:
        return None

    return {
        "numberLabel": _build_number_label(top["from_number__name"]),
        "count": top["count"],
    }


def get_messages_metrics_cards():
    inbound_count = WhatsappMessage.objects.count()
    categorized_count = WhatsappMessage.objects.filter(category__isnull=False).count()
    uncategorized_count = inbound_count - categorized_count

    top_category = _get_top_category_by_messages()
    top_inbound_number = _get_number_with_most_inbound()

    return [
        {
            "title": "Mensagens Recebidas",
            "value": inbound_count,
            "icon": "mdi-message-reply-text-outline",
            "color": "primary",
        },
        {
            "title": "Mensagens Sem Categoria",
            "value": uncategorized_count,
            "icon": "mdi-tag-off-outline",
            "color": "warning",
        },
        {
            "title": "Categoria Mais Usada",
            "value": (
                f"{top_category['categoryName']} • {top_category['numberLabel']} ({top_category['count']})"
                if top_category
                else "-"
            ),
            "icon": "mdi-trophy-variant-outline",
            "color": "success",
        },
        {
            "title": "Numero com Mais Recebidas",
            "value": (
                f"{top_inbound_number['numberLabel']} ({top_inbound_number['count']})"
                if top_inbound_number
                else "-"
            ),
            "icon": "mdi-cellphone-message",
            "color": "secondary",
        },
    ]
