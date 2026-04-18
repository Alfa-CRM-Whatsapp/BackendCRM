from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from core.crm.models import ContactWhatsapp, OutboundWhatsappMessage, WhatsappMessage, WhatsappNumber


def _percent_change(current, previous):
    if previous <= 0:
        if current <= 0:
            return 0.0
        return 100.0

    return round(((current - previous) / previous) * 100, 1)


def _format_delta_label(delta, suffix):
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta} {suffix}"


def _get_messages_last_7_days_series(today_local_date):
    start_date = today_local_date - timedelta(days=6)

    rows = (
        WhatsappMessage.objects
        .filter(created_at__date__gte=start_date, created_at__date__lte=today_local_date)
        .values("created_at__date")
        .annotate(count=Count("id"))
    )

    counts_by_date = {row["created_at__date"]: row["count"] for row in rows}

    series = []
    for offset in range(7):
        day = start_date + timedelta(days=offset)
        series.append(
            {
                "date": day.isoformat(),
                "label": day.strftime("%d/%m"),
                "messages": counts_by_date.get(day, 0),
            }
        )

    return series


def _get_messages_today_hourly_series(today_local_date):
    rows = (
        WhatsappMessage.objects
        .filter(created_at__date=today_local_date)
        .values("created_at__hour")
        .annotate(count=Count("id"))
    )

    counts_by_hour = {row["created_at__hour"]: row["count"] for row in rows}

    return [
        {
            "hour": hour,
            "label": f"{hour:02d}:00",
            "messages": counts_by_hour.get(hour, 0),
        }
        for hour in range(24)
    ]


def _get_outbound_health(today_local_date):
    statuses = ["sent", "delivered", "read", "failed"]
    rows = (
        OutboundWhatsappMessage.objects
        .filter(created_at__date=today_local_date)
        .values("status")
        .annotate(count=Count("id"))
    )

    counts = {status: 0 for status in statuses}
    for row in rows:
        status = row["status"]
        if status in counts:
            counts[status] = row["count"]

    total = sum(counts.values())
    if total > 0:
        delivery_rate = round(((counts["delivered"] + counts["read"]) / total) * 100, 1)
        read_rate = round((counts["read"] / total) * 100, 1)
        failed_rate = round((counts["failed"] / total) * 100, 1)
    else:
        delivery_rate = 0.0
        read_rate = 0.0
        failed_rate = 0.0

    return {
        "total": total,
        "counts": counts,
        "deliveryRate": delivery_rate,
        "readRate": read_rate,
        "failedRate": failed_rate,
    }


def _get_funnel_last_7_days(start_date):
    inbound_contacts = set(
        WhatsappMessage.objects
        .filter(created_at__date__gte=start_date)
        .values_list("contact_id", flat=True)
        .distinct()
    )
    outbound_contacts = set(
        OutboundWhatsappMessage.objects
        .filter(created_at__date__gte=start_date)
        .values_list("contact_id", flat=True)
        .distinct()
    )

    engaged = inbound_contacts.intersection(outbound_contacts)

    return {
        "inboundContacts": len(inbound_contacts),
        "engagedContacts": len(engaged),
        "outboundContacts": len(outbound_contacts),
    }


def _get_number_activity_last_7_days(start_date):
    inbound_rows = (
        WhatsappMessage.objects
        .filter(created_at__date__gte=start_date)
        .values("from_number_id", "from_number__name", "from_number__display_phone_number")
        .annotate(inboundCount=Count("id"))
    )

    grouped = {}
    for row in inbound_rows:
        number_id = row["from_number_id"]
        grouped[number_id] = {
            "numberId": number_id,
            "numberLabel": row["from_number__name"] or row["from_number__display_phone_number"] or "Sem numero",
            "inbound": row["inboundCount"],
            "outbound": 0,
        }

    outbound_rows = (
        OutboundWhatsappMessage.objects
        .filter(created_at__date__gte=start_date)
        .values("from_number_id", "from_number__name", "from_number__display_phone_number")
        .annotate(outboundCount=Count("id"))
    )

    for row in outbound_rows:
        number_id = row["from_number_id"]
        if number_id not in grouped:
            grouped[number_id] = {
                "numberId": number_id,
                "numberLabel": row["from_number__name"] or row["from_number__display_phone_number"] or "Sem numero",
                "inbound": 0,
                "outbound": row["outboundCount"],
            }
        else:
            grouped[number_id]["outbound"] = row["outboundCount"]

    result = []
    for item in grouped.values():
        total = item["inbound"] + item["outbound"]
        item["total"] = total
        result.append(item)

    result.sort(key=lambda x: (-x["total"], x["numberLabel"]))
    return result


def _get_category_distribution_by_number():
    rows = (
        WhatsappMessage.objects
        .filter(category__isnull=False)
        .values(
            "from_number_id",
            "from_number__name",
            "from_number__display_phone_number",
            "category__id",
            "category__name",
        )
        .annotate(count=Count("id"))
        .order_by("from_number__name", "category__name")
    )

    grouped = {}

    for row in rows:
        number_id = row["from_number_id"]
        if number_id not in grouped:
            label = row["from_number__name"] or row["from_number__display_phone_number"] or "Sem numero"
            grouped[number_id] = {
                "numberId": number_id,
                "numberLabel": label,
                "totalMessages": 0,
                "categories": [],
            }

        grouped[number_id]["categories"].append(
            {
                "categoryId": row["category__id"],
                "categoryName": row["category__name"],
                "count": row["count"],
            }
        )
        grouped[number_id]["totalMessages"] += row["count"]

    for number_data in grouped.values():
        total = number_data["totalMessages"] or 1
        for category_data in number_data["categories"]:
            category_data["percentage"] = round((category_data["count"] / total) * 100, 1)

        number_data["categories"] = sorted(
            number_data["categories"],
            key=lambda item: (-item["count"], item["categoryName"] or ""),
        )

    # Inclui numeros sem mensagens categorizadas para o front conseguir listar todos.
    existing_number_ids = set(grouped.keys())
    for number in WhatsappNumber.objects.all().order_by("name", "id"):
        if number.id in existing_number_ids:
            continue

        grouped[number.id] = {
            "numberId": number.id,
            "numberLabel": number.name or number.display_phone_number or "Sem numero",
            "totalMessages": 0,
            "categories": [],
        }

    return sorted(grouped.values(), key=lambda item: item["numberLabel"])


def get_dashboard_metrics():
    now = timezone.localtime()
    today = now.date()
    yesterday = today - timedelta(days=1)

    # Cards: Mensagens Hoje
    messages_today = WhatsappMessage.objects.filter(created_at__date=today).count()
    messages_yesterday = WhatsappMessage.objects.filter(created_at__date=yesterday).count()
    messages_delta = messages_today - messages_yesterday
    messages_delta_pct = _percent_change(messages_today, messages_yesterday)

    # Cards: Leads Hoje (contatos criados hoje)
    leads_today = ContactWhatsapp.objects.filter(created_at__date=today).count()
    leads_yesterday = ContactWhatsapp.objects.filter(created_at__date=yesterday).count()
    leads_delta = leads_today - leads_yesterday
    leads_delta_pct = _percent_change(leads_today, leads_yesterday)

    # Cards: Contatos Ativos (contatos com qualquer interação)
    inbound_contact_ids = set(WhatsappMessage.objects.values_list("contact_id", flat=True).distinct())
    outbound_contact_ids = set(OutboundWhatsappMessage.objects.values_list("contact_id", flat=True).distinct())
    active_contact_ids = inbound_contact_ids.union(outbound_contact_ids)
    active_contacts = len(active_contact_ids)

    week_start = today - timedelta(days=6)
    new_contacts_week = ContactWhatsapp.objects.filter(created_at__date__gte=week_start).count()

    prev_week_start = week_start - timedelta(days=7)
    prev_week_end = week_start - timedelta(days=1)
    prev_week_new_contacts = ContactWhatsapp.objects.filter(
        created_at__date__gte=prev_week_start,
        created_at__date__lte=prev_week_end,
    ).count()
    active_contacts_delta_pct = _percent_change(new_contacts_week, prev_week_new_contacts)

    # Cards: Taxa De Conversao (ultimos 7 dias)
    inbound_recent = set(
        WhatsappMessage.objects
        .filter(created_at__date__gte=week_start)
        .values_list("contact_id", flat=True)
        .distinct()
    )
    outbound_recent = set(
        OutboundWhatsappMessage.objects
        .filter(created_at__date__gte=week_start)
        .values_list("contact_id", flat=True)
        .distinct()
    )

    if inbound_recent:
        converted_count = len(inbound_recent.intersection(outbound_recent))
        conversion_rate = round((converted_count / len(inbound_recent)) * 100, 1)
    else:
        conversion_rate = 0.0

    prev_window_start = week_start - timedelta(days=7)
    prev_window_end = week_start - timedelta(days=1)

    inbound_prev = set(
        WhatsappMessage.objects
        .filter(created_at__date__gte=prev_window_start, created_at__date__lte=prev_window_end)
        .values_list("contact_id", flat=True)
        .distinct()
    )
    outbound_prev = set(
        OutboundWhatsappMessage.objects
        .filter(created_at__date__gte=prev_window_start, created_at__date__lte=prev_window_end)
        .values_list("contact_id", flat=True)
        .distinct()
    )

    if inbound_prev:
        converted_prev = len(inbound_prev.intersection(outbound_prev))
        conversion_prev = (converted_prev / len(inbound_prev)) * 100
    else:
        conversion_prev = 0.0

    conversion_delta_pct = _percent_change(conversion_rate, conversion_prev)

    messages_last_hour = WhatsappMessage.objects.filter(created_at__gte=now - timedelta(hours=1)).count()
    outbound_health_today = _get_outbound_health(today)
    funnel_last_7_days = _get_funnel_last_7_days(week_start)
    number_activity_last_7_days = _get_number_activity_last_7_days(week_start)
    verified_numbers = WhatsappNumber.objects.filter(verified=True).count()
    total_numbers = WhatsappNumber.objects.count()
    verification_rate = round((verified_numbers / total_numbers) * 100, 1) if total_numbers else 0.0

    return {
        "cards": [
            {
                "key": "messages_today",
                "title": "Mensagens Hoje",
                "value": messages_today,
                "changePercent": messages_delta_pct,
                "changeDescription": _format_delta_label(messages_delta, "em relacao a ontem"),
            },
            {
                "key": "leads_today",
                "title": "Leads Hoje",
                "value": leads_today,
                "changePercent": leads_delta_pct,
                "changeDescription": _format_delta_label(leads_delta, "novos leads captados"),
            },
            {
                "key": "active_contacts",
                "title": "Contatos Ativos",
                "value": active_contacts,
                "changePercent": active_contacts_delta_pct,
                "changeDescription": _format_delta_label(new_contacts_week, "novos esta semana"),
            },
            {
                "key": "conversion_rate",
                "title": "Taxa De Conversao",
                "value": conversion_rate,
                "valueSuffix": "%",
                "changePercent": conversion_delta_pct,
                "changeDescription": "Media dos ultimos 7 dias",
            },
            {
                "key": "delivery_rate_today",
                "title": "Taxa De Entrega Hoje",
                "value": outbound_health_today["deliveryRate"],
                "valueSuffix": "%",
                "changePercent": outbound_health_today["readRate"],
                "changeDescription": f"Falha {outbound_health_today['failedRate']}%",
            },
            {
                "key": "verified_numbers_rate",
                "title": "Numeros Verificados",
                "value": verification_rate,
                "valueSuffix": "%",
                "changePercent": 0.0,
                "changeDescription": f"{verified_numbers} de {total_numbers} numeros",
            },
        ],
        "messagesOverTime": {
            "title": "Mensagens Ao Longo Do Tempo",
            "range": "Ultimos 7 dias",
            "series": _get_messages_last_7_days_series(today),
            "todayHourly": _get_messages_today_hourly_series(today),
            "live": {
                "label": "Ao vivo",
                "messagesLastHour": messages_last_hour,
            },
        },
        "outboundHealthToday": outbound_health_today,
        "funnelLast7Days": funnel_last_7_days,
        "numberActivityLast7Days": number_activity_last_7_days,
        "categoryDistribution": {
            "title": "Categorias De Mensagens",
            "subtitle": "Distribuicao por categoria por numero",
            "numbers": _get_category_distribution_by_number(),
        },
    }
