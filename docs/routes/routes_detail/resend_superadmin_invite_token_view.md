# ResendSuperAdminInviteTokenView

- Route: /api/resend-token/
- View: ResendSuperAdminInviteTokenView

## Codigo Da View

Fonte: src\core\authentication\views\admin_invite.py

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, viewsets
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
import secrets

from core.authentication.serializers import ApproveSuperAdminInviteSerializer
from core.authentication.models import SuperAdminInvite, UserPreferences
from core.authentication.serializers import (
    SuperAdminInviteCreateSerializer,
    SuperAdminInviteListSerializer,
    ResendSuperAdminInviteSerializer
)

User = get_user_model()

class SuperAdminInviteViewSet(viewsets.ModelViewSet):
    queryset = SuperAdminInvite.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return SuperAdminInviteCreateSerializer
        return SuperAdminInviteListSerializer

    def get_queryset(self):
        if self.request.user.is_superadmin:
            return SuperAdminInvite.objects.all().order_by("-created_at")
        return SuperAdminInvite.objects.none()

    def create(self, request, *args, **kwargs):

        if not request.user.is_superadmin:
            return Response(
                {"error": "Apenas superadmins podem criar convites"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Já existe um usuário com este email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if SuperAdminInvite.objects.filter(email=email, used=False).exists():
            return Response(
                {"error": "Já existe um convite pendente para este email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invite = serializer.save()

        html_message = render_to_string(
            "emails/superadmin_invite.html",
            {
                "email": invite.email,
                "token": invite.token
            }
        )

        for email_admin in settings.ADMINS_EMAILS:
            send_mail(
                subject="Aprovação de novo SuperAdmin",
                message=f"Token para aprovar {invite.email}: {invite.token}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email_admin],
                html_message=html_message
            )

        return Response({
            "message": "Convite criado e enviado para aprovadores",
            "data": SuperAdminInviteListSerializer(invite).data,
            "code_status": status.HTTP_201_CREATED
        })
    
class ApproveSuperAdminInviteView(APIView):

    permission_classes = []

    @extend_schema(
        request=ApproveSuperAdminInviteSerializer,
        responses={200: dict}
    )
    def post(self, request):
        serializer = ApproveSuperAdminInviteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        token = serializer.validated_data["token"]

        try:
            invite = SuperAdminInvite.objects.get(email=email, token=token)
        except SuperAdminInvite.DoesNotExist:
            return Response(
                {"error": "Token Inválido, tente novamente ou reenvie o token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invite.approved = True
        invite.used = True
        invite.save()

        user = User.objects.create(
            email=invite.email,
            password=invite.password,
            is_superadmin=True,
            is_staff=True,
            is_superuser=True
        )

        UserPreferences.objects.create(user=user)

        return Response({
            "message": "SuperAdmin criado com sucesso",
            "email": user.email,
            "code_status": status.HTTP_200_OK
        })
    
class ResendSuperAdminInviteTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ResendSuperAdminInviteSerializer,
        responses={200: dict}
    )
    def post(self, request):
        # Verificar se é superadmin
        if not request.user.is_superadmin:
            return Response(
                {"error": "Apenas superadmins podem reenviar tokens"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ResendSuperAdminInviteSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        try:
            invite = SuperAdminInvite.objects.get(email=email, used=False)
        except SuperAdminInvite.DoesNotExist:
            return Response(
                {"error": "Nenhum convite pendente encontrado para este email"},
                status=status.HTTP_404_NOT_FOUND
            )

        def generate_invite_code():
           return str(secrets.randbelow(900000) + 100000)
        
        while True:
            new_token = generate_invite_code()
            if not SuperAdminInvite.objects.filter(token=new_token).exists():
                invite.token = new_token
                break

        invite.save()

        html_message = render_to_string(
            "emails/superadmin_invite.html",
            {
                "email": invite.email,
                "token": invite.token,
            }
        )

        for email_admin in settings.ADMINS_EMAILS:
            send_mail(
                subject="[REENVIO] Aprovação de novo SuperAdmin",
                message=f"Novo token para aprovar {invite.email}: {invite.token}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email_admin],
                html_message=html_message
            )

        return Response({
            "message": "Novo token gerado e enviado com sucesso",
            "email": invite.email,
            "code_status": status.HTTP_200_OK
        })
```
