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
        recipient_id = status_data.get("recipient_id")

        outbound_messages = OutboundWhatsappMessage.objects.filter(id_message=message_id)

        for outbound in outbound_messages:
            raw_response = outbound.raw_response if isinstance(outbound.raw_response, dict) else {}
            webhook_updates = raw_response.get("webhook_status_updates", [])

            if not isinstance(webhook_updates, list):
                webhook_updates = []

            webhook_update_entry = {
                "status": status_value,
                "timestamp": status_data.get("timestamp"),
                "recipient_id": status_data.get("recipient_id"),
                "errors": status_data.get("errors", []),
                "raw": status_data,
            }

            webhook_updates.append(webhook_update_entry)

            raw_response["last_webhook_status"] = webhook_update_entry
            raw_response["webhook_status_updates"] = webhook_updates

            outbound.status = status_value
            outbound.raw_response = raw_response
            outbound.save(update_fields=["status", "raw_response", "updated_at"])

        if not outbound_messages.exists() and recipient_id:
            contact, _ = ContactWhatsapp.objects.get_or_create(
                wa_id=recipient_id,
                defaults={
                    "profile_name": recipient_id,
                    "number": recipient_id,
                }
            )

            chat, _ = Chat.objects.get_or_create(
                contact=contact,
                from_number=whatsapp_number,
            )

            webhook_update_entry = {
                "status": status_value,
                "timestamp": status_data.get("timestamp"),
                "recipient_id": recipient_id,
                "errors": status_data.get("errors", []),
                "raw": status_data,
            }

            OutboundWhatsappMessage.objects.create(
                id_message=message_id,
                contact=contact,
                from_number=whatsapp_number,
                chat=chat,
                message={
                    "id": message_id,
                    "type": "unknown",
                    "source": "webhook_status",
                    "recipient_id": recipient_id,
                },
                status=status_value,
                with_template=False,
                raw_response={
                    "source": "webhook_status_fallback",
                    "last_webhook_status": webhook_update_entry,
                    "webhook_status_updates": [webhook_update_entry],
                },
            )

        print(f"📬 Status atualizado: {message_id} -> {status_value}")

        if status_value == "failed" and status_data.get("errors"):
            print(f"❌ Falha de entrega: {status_data.get('errors')}")