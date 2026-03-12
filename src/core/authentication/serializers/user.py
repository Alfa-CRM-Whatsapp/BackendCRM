from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, serializers
from core.authentication.models import User

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = "email"

class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'is_superadmin')

class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_superadmin=False
        )
        return user