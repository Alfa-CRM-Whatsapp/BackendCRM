from core.crm.models import (
    Chat,
    ContactWhatsapp,
    OutboundWhatsappMessage,
    WhatsappMessage,
    WhatsappNumber,
)


def handle_messages_field(value):
    metadata = value.get("metadata", {})
    phone_number_id = metadata.get("phone_number_id")

    whatsapp_number = WhatsappNumber.objects.get(
        phone_number_id=phone_number_id
    )

    if "messages" in value:
        message = value["messages"][0]
        contact_data = value["contacts"][0]

        contact_name = contact_data["profile"]["name"]
        wa_id = contact_data["wa_id"]
        number = message["from"]

        message_id = message["id"]
        message_type = message["type"]
        messaging_product = value["messaging_product"]

        contact, _ = ContactWhatsapp.objects.get_or_create(
            wa_id=wa_id,
            defaults={
                "profile_name": contact_name,
                "number": number,
            }
        )

        chat, _ = Chat.objects.get_or_create(
            contact=contact,
            from_number=whatsapp_number
        )

        WhatsappMessage.objects.create(
            id_message=message_id,
            type=message_type,
            messaging_product=messaging_product,
            contact=contact,
            from_number=whatsapp_number,
            chat=chat,
            messages=message
        )

        print("📨 Mensagem salva e enviada ao signal")

    elif "statuses" in value:
        status_data = value["statuses"][0]

        message_id = status_data["id"]
        status_value = status_data["status"]

        OutboundWhatsappMessage.objects.filter(
            id_message=message_id
        ).update(
            status=status_value
        )

        print(f"📬 Status atualizado: {message_id} -> {status_value}")