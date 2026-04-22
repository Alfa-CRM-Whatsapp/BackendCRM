import requests
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.crm.models import WhatsappNumber
from core.crm.serializers import (
    EmbeddedSignupCompleteSerializer,
    EmbeddedSignupExchangeCodeSerializer,
    EmbeddedSignupSubscribeSerializer,
    EmbeddedSignupSyncNumbersSerializer,
    EmbeddedSignupWabaListSerializer,
)


GRAPH_VERSION = "v25.0"
logger = logging.getLogger(__name__)


class EmbeddedSignupCallbackView(APIView):
    # Recebe o code do OAuth da Meta para o frontend continuar o fluxo.
    def get(self, request: Request) -> Response:
        try:
            code = request.GET.get("code")

            if not code:
                logger.warning("Embedded Signup callback sem code.")
                return Response(
                    {
                        "success": False,
                        "error": "code not provided",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info("Embedded Signup callback recebido com code.")
            return Response(
                {
                    "success": True,
                    "code": code,
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Erro ao processar callback do Embedded Signup.")
            return Response(
                {
                    "success": False,
                    "error": "internal error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def _resolve_access_token(requested_token):
    token = requested_token or settings.ACCESS_TOKEN
    if not token:
        return None
    return token


def _sync_numbers_from_meta(waba_id, access_token, language="pt_BR"):
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{waba_id}/phone_numbers"
    params = {
        "fields": "id,display_phone_number,verified_name,name_status,code_verification_status,quality_rating,status",
    }

    response = requests.get(
        url,
        params=params,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )

    payload = response.json()

    if response.status_code != 200:
        return None, payload, response.status_code

    rows = payload.get("data", [])

    created_count = 0
    updated_count = 0
    synced_numbers = []

    for row in rows:
        phone_number_id = row.get("id")

        if not phone_number_id:
            continue

        display_phone_number = row.get("display_phone_number") or ""
        verified_name = row.get("verified_name") or display_phone_number or "WhatsApp"

        status_from_meta = (
            row.get("code_verification_status")
            or row.get("status")
            or "PENDING"
        )

        verified = str(status_from_meta).upper() in {"VERIFIED", "CONNECTED"}

        obj, created = WhatsappNumber.objects.update_or_create(
            phone_number_id=phone_number_id,
            defaults={
                "display_phone_number": display_phone_number,
                "waba_id": str(waba_id),
                "name": verified_name,
                "language": language,
                "status": status_from_meta,
                "verified": verified,
            },
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

        synced_numbers.append(
            {
                "id": obj.id,
                "phone_number_id": obj.phone_number_id,
                "display_phone_number": obj.display_phone_number,
                "name": obj.name,
                "status": obj.status,
                "verified": obj.verified,
            }
        )

    return (
        {
            "waba_id": str(waba_id),
            "total_meta_numbers": len(rows),
            "created": created_count,
            "updated": updated_count,
            "numbers": synced_numbers,
        },
        payload,
        status.HTTP_200_OK,
    )


class EmbeddedSignupExchangeCodeView(APIView):
    def post(self, request):
        serializer = EmbeddedSignupExchangeCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        app_id = settings.META_APP_ID
        app_secret = settings.META_APP_SECRET

        if not app_id or not app_secret:
            return Response(
                {
                    "error": "META_APP_ID e META_APP_SECRET sao obrigatorios para trocar o code do Embedded Signup.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        params = {
            "client_id": app_id,
            "client_secret": app_secret,
            "code": serializer.validated_data["code"],
        }

        redirect_uri = serializer.validated_data.get("redirect_uri")
        if redirect_uri:
            params["redirect_uri"] = redirect_uri

        response = requests.get(
            f"https://graph.facebook.com/{GRAPH_VERSION}/oauth/access_token",
            params=params,
            timeout=30,
        )

        data = response.json()

        if response.status_code != 200:
            return Response(data, status=response.status_code)

        return Response(
            {
                "access_token": data.get("access_token"),
                "token_type": data.get("token_type"),
                "expires_in": data.get("expires_in"),
            },
            status=status.HTTP_200_OK,
        )


class EmbeddedSignupWabaListView(APIView):
    def post(self, request):
        serializer = EmbeddedSignupWabaListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = _resolve_access_token(serializer.validated_data.get("access_token"))

        if not access_token:
            return Response(
                {"error": "ACCESS_TOKEN nao configurado e nenhum access_token foi enviado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = requests.get(
            f"https://graph.facebook.com/{GRAPH_VERSION}/me/whatsapp_business_accounts",
            params={"fields": "id,name,currency,timezone_id"},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )

        data = response.json()

        if response.status_code != 200:
            return Response(data, status=response.status_code)

        return Response(data, status=status.HTTP_200_OK)


class EmbeddedSignupSubscribeAppView(APIView):
    def post(self, request):
        serializer = EmbeddedSignupSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        waba_id = serializer.validated_data["waba_id"]
        access_token = _resolve_access_token(serializer.validated_data.get("access_token"))

        if not access_token:
            return Response(
                {"error": "ACCESS_TOKEN nao configurado e nenhum access_token foi enviado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = requests.post(
            f"https://graph.facebook.com/{GRAPH_VERSION}/{waba_id}/subscribed_apps",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )

        data = response.json()

        if response.status_code != 200:
            return Response(data, status=response.status_code)

        return Response(
            {
                "waba_id": str(waba_id),
                "subscribed": bool(data.get("success")),
                "meta_response": data,
            },
            status=status.HTTP_200_OK,
        )


class EmbeddedSignupSyncNumbersView(APIView):
    def post(self, request):
        serializer = EmbeddedSignupSyncNumbersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        waba_id = serializer.validated_data["waba_id"]
        access_token = _resolve_access_token(serializer.validated_data.get("access_token"))

        if not access_token:
            return Response(
                {"error": "ACCESS_TOKEN nao configurado e nenhum access_token foi enviado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload, error_payload, status_code = _sync_numbers_from_meta(
            waba_id=waba_id,
            access_token=access_token,
            language=serializer.validated_data.get("language", "pt_BR"),
        )

        if status_code != status.HTTP_200_OK:
            return Response(error_payload, status=status_code)

        return Response(payload, status=status.HTTP_200_OK)


class EmbeddedSignupCompleteView(APIView):
    def post(self, request):
        serializer = EmbeddedSignupCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        waba_id = serializer.validated_data["waba_id"]
        access_token = _resolve_access_token(serializer.validated_data.get("access_token"))
        subscribe_app = serializer.validated_data.get("subscribe_app", True)
        language = serializer.validated_data.get("language", "pt_BR")

        if not access_token:
            return Response(
                {"error": "ACCESS_TOKEN nao configurado e nenhum access_token foi enviado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscribe_result = None

        if subscribe_app:
            subscribe_response = requests.post(
                f"https://graph.facebook.com/{GRAPH_VERSION}/{waba_id}/subscribed_apps",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30,
            )
            subscribe_data = subscribe_response.json()

            subscribe_result = {
                "ok": subscribe_response.status_code == 200,
                "meta_status": subscribe_response.status_code,
                "meta_response": subscribe_data,
            }

        sync_result, error_payload, status_code = _sync_numbers_from_meta(
            waba_id=waba_id,
            access_token=access_token,
            language=language,
        )

        if status_code != status.HTTP_200_OK:
            return Response(
                {
                    "waba_id": str(waba_id),
                    "subscribe_result": subscribe_result,
                    "sync_error": error_payload,
                },
                status=status_code,
            )

        return Response(
            {
                "waba_id": str(waba_id),
                "subscribe_result": subscribe_result,
                "sync_result": sync_result,
            },
            status=status.HTTP_200_OK,
        )