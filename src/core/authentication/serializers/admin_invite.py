from rest_framework import serializers
from core.authentication.models import SuperAdminInvite
from django.contrib.auth.hashers import make_password

class SuperAdminInviteSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperAdminInvite
        fields = ["email", "password"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)
    
class ApproveSuperAdminInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.UUIDField()