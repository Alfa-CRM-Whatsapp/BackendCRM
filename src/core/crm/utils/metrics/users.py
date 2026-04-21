from datetime import timedelta

from django.utils import timezone

from core.authentication.models import SuperAdminInvite, User


def _percent_change(current, previous):
    if previous <= 0:
        if current <= 0:
            return 0.0
        return 100.0

    return round(((current - previous) / previous) * 100, 1)


def _format_delta_label(delta, suffix):
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta} {suffix}"


def get_users_metrics_cards():
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    superadmins_count = User.objects.filter(is_superadmin=True).count()

    users_today = User.objects.filter(date_joined__date=today).count()
    users_yesterday = User.objects.filter(date_joined__date=yesterday).count()
    users_delta = users_today - users_yesterday
    users_delta_pct = _percent_change(users_today, users_yesterday)

    invites_total = SuperAdminInvite.objects.count()
    invites_pending = SuperAdminInvite.objects.filter(used=False).count()
    invites_approved = SuperAdminInvite.objects.filter(approved=True).count()

    invites_today = SuperAdminInvite.objects.filter(created_at__date=today).count()
    invites_yesterday = SuperAdminInvite.objects.filter(created_at__date=yesterday).count()
    invites_delta = invites_today - invites_yesterday
    invites_delta_pct = _percent_change(invites_today, invites_yesterday)

    approval_rate = round((invites_approved / invites_total) * 100, 1) if invites_total else 0.0

    return [
        {
            "title": "Usuarios Totais",
            "value": total_users,
            "icon": "mdi-account-multiple",
            "color": "primary",
        },
        {
            "title": "Usuarios Ativos",
            "value": active_users,
            "icon": "mdi-account-check-outline",
            "color": "success",
        },
        {
            "title": "Superadmins",
            "value": superadmins_count,
            "icon": "mdi-shield-account-outline",
            "color": "info",
        },
        {
            "title": "Novos Usuarios Hoje",
            "value": users_today,
            "icon": "mdi-account-plus-outline",
            "color": "secondary",
            "changePercent": users_delta_pct,
            "changeDescription": _format_delta_label(users_delta, "em relacao a ontem"),
        },
        {
            "title": "Convites De Superadmin Pendentes",
            "value": invites_pending,
            "icon": "mdi-email-alert-outline",
            "color": "warning",
        },
        {
            "title": "Convites Criados Hoje",
            "value": invites_today,
            "icon": "mdi-email-plus-outline",
            "color": "primary",
            "changePercent": invites_delta_pct,
            "changeDescription": _format_delta_label(invites_delta, "em relacao a ontem"),
        },
        {
            "title": "Taxa De Aprovacao De Convites",
            "value": approval_rate,
            "valueSuffix": "%",
            "icon": "mdi-badge-account-horizontal-outline",
            "color": "success",
            "changeDescription": f"{invites_approved} aprovados de {invites_total}",
        },
    ]
