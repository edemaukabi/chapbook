from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django_countries.serializer_fields import CountryField
import logging

logger = logging.getLogger(__name__)
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

User = get_user_model()


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def save(self):
        email = self.validated_data["email"]
        active_users = User.objects.filter(email__iexact=email, is_active=True)

        for user in active_users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

            html_body = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0d1117;font-family:Arial,sans-serif;">
  <div style="max-width:520px;margin:40px auto;background:#161b22;border:1px solid #30363d;border-radius:12px;padding:40px;">
    <h2 style="color:#e6edf3;margin:0 0 8px;">Reset your Chapbook password</h2>
    <p style="color:#8b949e;margin:0 0 28px;line-height:1.6;">
      Click the button below to choose a new password. This link expires in 1 hour.
    </p>
    <a href="{reset_url}" style="display:inline-block;background:linear-gradient(135deg,#6e40c9,#8b5cf6);color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:700;font-size:0.95rem;">
      Reset password
    </a>
    <p style="margin-top:28px;color:#484f58;font-size:0.85rem;line-height:1.6;">
      If you didn't request this, you can safely ignore this email.
    </p>
    <hr style="border:none;border-top:1px solid #21262d;margin:28px 0 16px;">
    <p style="color:#484f58;font-size:0.8rem;text-align:center;margin:0;">Chapbook — where stories live</p>
  </div>
</body></html>"""
            plain = strip_tags(html_body)
            msg = EmailMultiAlternatives(
                subject="Reset your Chapbook password",
                body=plain,
                from_email=f"Chapbook <{settings.DEFAULT_FROM_EMAIL}>",
                to=[email],
            )
            msg.attach_alternative(html_body, "text/html")
            try:
                msg.send()
                logger.info(f"Password reset email sent to: {email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email to {email}: {e}")



class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="profile.gender")
    phone_number = PhoneNumberField(source="profile.phone_number")
    profile_photo = serializers.ReadOnlyField(source="profile.profile_photo.url")
    country = CountryField(source="profile.country")
    city = serializers.CharField(source="profile.city")

    class Meta:
        model = User
        fields = [
            "pk",
            "id",
            "email",
            "first_name",
            "last_name",
            "gender",
            "phone_number",
            "profile_photo",
            "country",
            "city",
        ]

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        if instance.is_superuser:
            representation["admin"] = True
        return representation


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def get_cleaned_data(self):
        super().get_cleaned_data()
        return {
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password1": self.validated_data.get("password1", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self)
        user.save()

        setup_user_email(request, user, [])
        user.email = self.cleaned_data.get("email")
        user.password = self.cleaned_data.get("password1")
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")

        return user
