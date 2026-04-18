from rest_framework_simplejwt.views import TokenObtainPairView
from core.authentication.serializers import EmailTokenObtainPairSerializer, UserListSerializer, UserCreateSerializer, UserPreferencesSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserListSerializer.Meta.model.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer
    
class UserPreferencesViewSet(viewsets.ModelViewSet):
    queryset = UserPreferencesSerializer.Meta.model.objects.all()
    serializer_class = UserPreferencesSerializer


class IsSuperAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "is_superadmin": bool(request.user.is_superadmin),
                "user_id": request.user.id,
                "email": request.user.email,
            }
        )