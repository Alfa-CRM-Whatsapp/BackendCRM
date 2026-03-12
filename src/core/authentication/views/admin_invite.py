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

from core.authentication.serializers import SuperAdminInviteSerializer
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
            return Response({"error": "Apenas superadmins podem criar convites"}, status=403)

        serializer = SuperAdminInviteSerializer(data=request.data)

        if serializer.is_valid():

            invite = serializer.save()

            approve_link = f"http://localhost:8000/api/superadmin/approve/{invite.token}"

            html_message = render_to_string(
                "emails/superadmin_invite.html",
                {
                    "email": invite.email,
                    "approve_link": approve_link
                }
            )

            for email in settings.ADMINS_EMAILS:

                send_mail(
                    subject="Aprovação de novo SuperAdmin",
                    message=f"Acesse o link para aprovar: {approve_link}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message
                )

            return Response({
                "message": "Convite criado e enviado para aprovadores"
            })

        return Response(serializer.errors, status=400)
    
class ApproveSuperAdminInviteView(APIView):

    permission_classes = []

    def get(self, request, token):

        try:
            invite = SuperAdminInvite.objects.get(token=token)
        except SuperAdminInvite.DoesNotExist:
            return render(request, "invite_invalid.html")

        if invite.approved:
            return render(request, "invite_used.html")

        return render(request, "approve_invite.html", {
            "token": token,
            "email": invite.email
        })

    def post(self, request, token):

        try:
            invite = SuperAdminInvite.objects.get(token=token)
        except SuperAdminInvite.DoesNotExist:
            return render(request, "invite_invalid.html")

        if invite.approved:
            return render(request, "invite_used.html")

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

        return render(request, "invite_success.html", {
            "email": user.email
        })