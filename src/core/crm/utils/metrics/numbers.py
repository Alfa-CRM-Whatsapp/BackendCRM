from django.db.models import Count

from core.crm.models import MessageCategory, OutboundWhatsappMessage, WhatsappMessage, WhatsappNumber


def _build_number_label(name):
    return name or "Sem numero"


def _get_top_number_by_categories():
    top = (
        MessageCategory.objects
        .values(
            "whatsapp_number_id",
            "whatsapp_number__name",
        )
        .annotate(count=Count("id"))
        .order_by("-count", "whatsapp_number__name")
        .first()
    )

    if not top:
        return None

    return {
        "numberLabel": _build_number_label(top["whatsapp_number__name"]),
        "count": top["count"],
    }


def _get_top_number_by_messages():
    inbound = {
        row["from_number_id"]: {
            "name": row["from_number__name"],
            "count": row["count"],
        }
        for row in (
            WhatsappMessage.objects
            .values("from_number_id", "from_number__name")
            .annotate(count=Count("id"))
        )
    }

    outbound = (
        OutboundWhatsappMessage.objects
        .values("from_number_id", "from_number__name")
        .annotate(count=Count("id"))
    )

    for row in outbound:
        item = inbound.get(row["from_number_id"])
        if item:
            item["count"] += row["count"]
        else:
            inbound[row["from_number_id"]] = {
                "name": row["from_number__name"],
                "count": row["count"],
            }

    if not inbound:
        return None

    top = max(inbound.values(), key=lambda value: value["count"])

    return {
        "numberLabel": _build_number_label(top["name"]),
        "count": top["count"],
    }


def get_numbers_metrics_cards():
    total_numbers = WhatsappNumber.objects.count()
    verified_numbers = WhatsappNumber.objects.filter(verified=True).count()

    top_by_categories = _get_top_number_by_categories()
    top_by_messages = _get_top_number_by_messages()

    return [
        {
            "title": "Numeros Cadastrados",
            "value": total_numbers,
            "icon": "mdi-cellphone-link",
            "color": "primary",
        },
        {
            "title": "Numeros Verificados",
            "value": verified_numbers,
            "icon": "mdi-check-decagram-outline",
            "color": "success",
        },
        {
            "title": "Numero com Mais Categorias",
            "value": (
                f"{top_by_categories['numberLabel']} ({top_by_categories['count']})"
                if top_by_categories
                else "-"
            ),
            "icon": "mdi-shape-plus-outline",
            "color": "info",
        },
        {
            "title": "Numero com Mais Mensagens",
            "value": (
                f"{top_by_messages['numberLabel']} ({top_by_messages['count']})"
                if top_by_messages
                else "-"
            ),
            "icon": "mdi-message-outline",
            "color": "warning",
        },
    ]
