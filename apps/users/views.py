from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group


from .serializers import GoogleIDTokenSerializer, AdminUserSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from apps.roles.permissions import HasRole

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
        
        # 2) Assign a default role to the user ** We can use signals to automate it. But later **
        if created:
            default_role, _ = Group.objects.get_or_create(name='User')
            user.groups.add(default_role)

        # 3) Optional: update names if blank
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
        
        # 4) Checking if the user has been deactivated
        if not user.is_active:
            return Response({"detail": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)
        
        # 5) Serializing User with roles and permissions
        user_data = UserSerializer(user, context={"request": request}).data

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
            "user": user_data,
        }, status=status.HTTP_200_OK)
        
class AdminUserViewSet(viewsets.ModelViewSet):
    """
        Full CRUD for users by Admins or Managers
    """
    queryset = User.objects.all().order_by("-id")
    serializer_class = AdminUserSerializer
    permission_classes = [ IsAuthenticated, HasRole(["Admin"])]
    
    def destroy(self, request, *args, **kwargs):
        """
            Users soft delete
        """
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"detail": f"User {user.email} deactivated."}, status=status.HTTP_200_OK)