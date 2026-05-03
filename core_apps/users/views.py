import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomUserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.none()


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uid = request.data.get("uid", "")
        token = request.data.get("token", "")
        new_password1 = request.data.get("new_password1", "")
        new_password2 = request.data.get("new_password2", "")

        if not all([uid, token, new_password1, new_password2]):
            return Response(
                {"detail": "uid, token, new_password1, and new_password2 are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pkid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pkid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            logger.warning("Password reset confirm: invalid uid %r", uid)
            return Response(
                {"uid": ["Invalid value"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            logger.warning(
                "Password reset confirm: invalid token for user pkid=%s", user.pkid
            )
            return Response(
                {"token": ["Invalid value"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password1 != new_password2:
            return Response(
                {"new_password2": ["The two password fields didn't match."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password1) < 8:
            return Response(
                {"new_password1": ["Password must be at least 8 characters."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password1)
        user.save()
        logger.info("Password reset successfully for user pkid=%s", user.pkid)
        return Response(
            {"detail": "Password has been reset with the new password."},
            status=status.HTTP_200_OK,
        )
