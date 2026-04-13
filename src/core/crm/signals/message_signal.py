from django.db.models.signals import post_save
from django.dispatch import receiver

from core.crm.models import WhatsappMessage
from core.crm.utils.message_classifier import classify_message


@receiver(post_save, sender=WhatsappMessage)
def classify_message_signal(sender, instance, created, **kwargs):
    if not created:
        return

    print("📨 Mensagem enviada ao signal")

    if instance.type != "text":
        return

    try:
        message_text = instance.messages.get("text", {}).get("body", "")

        if not message_text.strip():
            return

        category, confidence = classify_message(
            message_text=message_text,
            whatsapp_number_id=instance.from_number.phone_number_id
        )

        instance.category = category
        instance.category_confidence = confidence
        instance.save(update_fields=["category", "category_confidence"])

        print(
            f"🏷️ [SIGNAL] Classificado: "
            f"{category.name if category else 'None'} "
            f"({confidence:.2f})"
        )

    except Exception as e:
        print("❌ Erro no SIGNAL:", str(e))