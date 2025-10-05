from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import GoogleIDTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# Storing Google link with allauth
try:
    from allauth.socialaccount.models import SocialAccount
    HAS_ALLAUTH_SOCIAL = True
except Exception:
    HAS_ALLAUTH_SOCIAL = False

User = get_user_model()


class GoogleVerifyView(APIView):
    """
    POST /api/auth/google/verify/
    Body: { "id_token": "<Google ID token>" }
    Returns: { access, refresh, user: {...} }
    """
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        ser = GoogleIDTokenSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)

        email = ser.validated_data["email"]
        first_name = ser.validated_data.get("first_name", "")
        last_name = ser.validated_data.get("last_name", "")
        google_sub = ser.validated_data.get("google_sub")

        # 1) Get or create local user by email
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"first_name": first_name, "last_name": last_name, "is_active": True},
        )

        # Optional: update names if blank
        if not created:
            changed = False
            if first_name and not user.first_name:
                user.first_name = first_name
                changed = True
            if last_name and not user.last_name:
                user.last_name = last_name
                changed = True
            if changed:
                user.save(update_fields=["first_name", "last_name"])

        if not user.is_active:
            return Response({"detail": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)

        # 2) (Optional) record Google link in allauth's SocialAccount
        #     This is nice for audits and to prevent duplicate links.
        if HAS_ALLAUTH_SOCIAL and google_sub:
            SocialAccount.objects.get_or_create(
                user=user,
                provider="google",
                uid=str(google_sub),
                defaults={"extra_data": {"email": email}},
            )

        # 3) Issue your own JWTs
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # 4) Return what frontend needs
        return Response({
            "access": str(access),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }, status=status.HTTP_200_OK)
