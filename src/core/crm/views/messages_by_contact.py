from itertools import chain
from datetime import datetime

from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.crm.models import WhatsappMessage, ContactWhatsapp
from core.crm.models import OutboundWhatsappMessage

from core.crm.serializers import WhatsappMessageListSerializer
from core.crm.serializers import OutboundWhatsappMessageListSerializer


class WhatsappMessageByNumberAndContactView(APIView):

    def get(self, request, number_id, wa_id):

        try:
            contact = ContactWhatsapp.objects.get(wa_id=wa_id)
        except ContactWhatsapp.DoesNotExist:
            return Response(
                {"error": "Contato não encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        inbound = (
            WhatsappMessage.objects
            .filter(from_number_id=number_id, contact=contact)
            .select_related("contact", "from_number")
        )

        outbound = (
            OutboundWhatsappMessage.objects
            .filter(from_number_id=number_id, contact=contact)
            .select_related("contact", "from_number")
        )

        inbound_data = WhatsappMessageListSerializer(inbound, many=True).data
        outbound_data = OutboundWhatsappMessageListSerializer(outbound, many=True).data

        def parse_date(msg):
            if msg.get("created_at"):
                dt = datetime.fromisoformat(msg["created_at"])
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                return dt

            elif msg.get("timestamp"):
                return datetime.fromtimestamp(int(msg["timestamp"]), tz=timezone.utc)

            return timezone.now()

        for msg in inbound_data:
            msg["direction"] = "inbound"
            msg["_date"] = parse_date(msg)

        for msg in outbound_data:
            msg["direction"] = "outbound"
            msg["_date"] = parse_date(msg)

        combined = list(chain(inbound_data, outbound_data))

        combined_sorted = sorted(combined, key=lambda x: x["_date"])

        for msg in combined_sorted:
            msg.pop("_date", None)

        return Response(combined_sorted, status=status.HTTP_200_OK)