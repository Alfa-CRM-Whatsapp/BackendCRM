from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, serializers
from core.authentication.models import User, UserPreferences

class UserPreferencesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPreferences
        fields = ('id', 'user', 'theme', 'primary_color')

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        preferences = getattr(user, "preferences", None)

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "is_superadmin": user.is_superadmin,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "preferences": UserPreferencesSerializer(preferences).data if preferences else None
        }

        return data

class UserListSerializer(serializers.ModelSerializer):

    preferences = UserPreferencesSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'is_superadmin', 'preferences')

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

        UserPreferences.objects.create(user=user)
    
        return user
        