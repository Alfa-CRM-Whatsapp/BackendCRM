from django.utils import timezone

from core.crm.models import WhatsappNumber


def _resolve_target_numbers(entry_id, value):
    waba_info = value.get("waba_info", {})
    waba_id = waba_info.get("waba_id") or entry_id

    queryset = WhatsappNumber.objects.none()

    if waba_id:
        queryset = WhatsappNumber.objects.filter(waba_id=str(waba_id))

    if not queryset.exists():
        queryset = WhatsappNumber.objects.all()

    return queryset, str(waba_id) if waba_id else None


def handle_account_update_field(value, entry_id=None):
    event = value.get("event")
    waba_info = value.get("waba_info", {})
    violation_info = value.get("violation_info", {})
    ban_info = value.get("ban_info", {})

    numbers, resolved_waba_id = _resolve_target_numbers(entry_id, value)

    for number in numbers:
        number.waba_id = resolved_waba_id or number.waba_id
        number.status = event or number.status
        number.account_event = event
        number.account_country = value.get("country") or number.account_country
        number.account_violation_type = (
            violation_info.get("violation_type") or number.account_violation_type
        )
        number.account_ban_state = ban_info.get("waba_ban_state") or number.account_ban_state
        number.account_ban_date = ban_info.get("waba_ban_date") or number.account_ban_date
        number.account_ad_account_id = (
            waba_info.get("ad_account_linked") or number.account_ad_account_id
        )
        number.account_owner_business_id = (
            waba_info.get("owner_business_id") or number.account_owner_business_id
        )

        if "auth_international_rate_eligibility" in value:
            number.auth_international_rate_eligibility = value.get(
                "auth_international_rate_eligibility"
            ) or {}

        if "volume_tier_info" in value:
            number.volume_tier_info = value.get("volume_tier_info") or {}

        if event in {"ACCOUNT_DELETED", "ACCOUNT_OFFBOARDED", "PARTNER_APP_UNINSTALLED"}:
            number.verified = False
        elif event in {"ACCOUNT_RECONNECTED"}:
            number.verified = True

        if number.account_ban_state == "DISABLE":
            number.verified = False
        elif number.account_ban_state == "REINSTATE":
            number.verified = True

        number.account_update_payload = value
        number.account_updated_at = timezone.now()
        number.save()

    print(f"🏢 Account update processado: event={event}, numbers={numbers.count()}")