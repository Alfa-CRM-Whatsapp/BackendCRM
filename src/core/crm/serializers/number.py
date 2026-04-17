from rest_framework import serializers
from core.crm.models import WhatsappNumber

class WhatsappNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = WhatsappNumber
        fields = [
            'id',
            'display_phone_number',
            'phone_number_id',
            'waba_id',
            'name',
            'language',
            'pin',
            'status',
            'account_event',
            'account_country',
            'account_violation_type',
            'account_ban_state',
            'account_ban_date',
            'account_ad_account_id',
            'account_owner_business_id',
            'auth_international_rate_eligibility',
            'volume_tier_info',
            'account_update_payload',
            'account_updated_at',
            'verified',
        ]