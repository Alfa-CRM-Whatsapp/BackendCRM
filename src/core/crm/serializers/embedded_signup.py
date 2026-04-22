from rest_framework import serializers


class EmbeddedSignupExchangeCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    redirect_uri = serializers.CharField(required=False, allow_blank=True)


class EmbeddedSignupWabaListSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False, allow_blank=True)


class EmbeddedSignupSyncNumbersSerializer(serializers.Serializer):
    waba_id = serializers.CharField()
    access_token = serializers.CharField(required=False, allow_blank=True)
    language = serializers.ChoiceField(
        choices=["pt_BR", "en_US"],
        required=False,
        default="pt_BR",
    )


class EmbeddedSignupSubscribeSerializer(serializers.Serializer):
    waba_id = serializers.CharField()
    access_token = serializers.CharField(required=False, allow_blank=True)


class EmbeddedSignupCompleteSerializer(serializers.Serializer):
    waba_id = serializers.CharField()
    access_token = serializers.CharField(required=False, allow_blank=True)
    subscribe_app = serializers.BooleanField(required=False, default=True)
    language = serializers.ChoiceField(
        choices=["pt_BR", "en_US"],
        required=False,
        default="pt_BR",
    )