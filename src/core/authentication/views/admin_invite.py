from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.template.loader import render_to_string

from core.authentication.serializers import SuperAdminInviteSerializer, ApproveSuperAdminInviteSerializer
from core.authentication.models import SuperAdminInvite

User = get_user_model()

class CreateSuperAdminInviteView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SuperAdminInviteSerializer,
        responses={200: dict}
    )
    def post(self, request):

        if not request.user.is_superadmin:
            return Response(
                {"error": "Apenas superadmins podem criar convites"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SuperAdminInviteSerializer(data=request.data)

        if serializer.is_valid():

            invite = serializer.save()

            html_message = render_to_string(
                "emails/superadmin_invite.html",
                {
                    "email": invite.email,
                    "token": invite.token
                }
            )

            for email in settings.ADMINS_EMAILS:

                send_mail(
                    subject="Aprovação de novo SuperAdmin",
                    message=f"Token para aprovar {invite.email}: {invite.token}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message
                )

            return Response({
                "message": "Convite criado e enviado para aprovadores"
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
                {"error": "Token ou email inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invite.approved:
            return Response(
                {"error": "Convite já foi aprovado"},
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

        return Response({
            "message": "SuperAdmin criado com sucesso",
            "email": user.email
        })