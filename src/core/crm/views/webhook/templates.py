from django.utils import timezone

from core.crm.models import WhatsAppTemplate


def handle_template_status_update(value):
    template_id = value.get("message_template_id")
    status = value.get("event")
    reason = value.get("reason")

    template = WhatsAppTemplate.objects.filter(
        meta_template_id=template_id
    ).first()

    if template:
        template.status = status

        if status == "APPROVED":
            template.approved_at = timezone.now()

        if status == "REJECTED":
            template.rejection_reason = reason

        template.save()

        print(f"📦 Template atualizado: {template.name} -> {status}")


def handle_template_category_update(value):
    template_id = value.get("message_template_id")
    new_category = value.get("new_category")

    template = WhatsAppTemplate.objects.filter(
        meta_template_id=template_id
    ).first()

    if template and new_category:
        template.category = new_category.lower()
        template.save()

        print(f"🔄 Categoria atualizada: {template.name} -> {new_category}")