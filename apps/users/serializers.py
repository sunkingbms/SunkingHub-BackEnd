from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Permission
from django.conf import settings

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField(required=True)
    
    def get_cleaned_data(self):
        return{
            "email": self.validated_data.get('email', ''),
            "password1": self.validated_data.get('password1', ''),
            "password2": self.validated_data.get('password2', ''),
        }
        
class CustomLoginSerializer(LoginSerializer):
    username = None
    
    def authenticate(self, **kwargs):
        """

        Overriding authenticate to use only email and password for login purpose
    
        """
        email = kwargs.get("email")
        password = kwargs.get("password")
        
        if email and password:
            user = authenticate(self.context["request"], email=email, password=password)
            if user:
                return user
            msg = 'Unable to login with provided credentials'
            raise serializers.ValidationError(msg)
        
class GoogleIDTokenSerializer(serializers.Serializer):
    id_token = serializers.CharField(write_only=True)
        
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    picture = serializers.URLField(read_only=True)
        
    def validate(self, attrs):
        raw_token = attrs.get("id_token")
        if not raw_token:
            raise serializers.ValidationError("id_token is required")
        # Verify signature + claims using Google's public key
        try:
            request = google_requests.Request()
            claims = google_id_token.verify_oauth2_token(raw_token, request)
        except Exception:
            raise serializers.ValidationError("Invalid Google ID token")
            
        # --- Core claims check ---
        aud = claims.get("aud")
        iss = claims.get("iss")
        email = claims.get("email")
        email_verified = claims.get("email_verified", False)
            
        if aud != settings.GOOGLE_CLIENT_ID:
            raise serializers.ValidationError("Google token audience mismatch.")
            
        if iss not in getattr(settings, "GOOGLE_ISSUERS", {"https://accounts.google.com", "accounts.google.com"}):
            raise serializers.ValidationError("Invalid token issuer.")

        if not email or not email_verified:
            raise serializers.ValidationError("Email not present/verified by Google.")
            
        # Optional profile fields
        given_name = claims.get("given_name", "")
        family_name = claims.get("family_name", "")
        picture = claims.get("picture", "")
        sub = claims.get("sub")  # Google's stable user id

        # Stash what we need for the view
        attrs.update({
            "claims": claims,
            "email": email,
            "first_name": given_name,
            "last_name": family_name,
            "picture": picture,
            "google_sub": sub,
        })
        return attrs

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [ "id", "email", "first_name", "last_name", "roles", "permissions"]
        
    def get_roles(self, obj):
        """
            Return an array of groups (roles) that belongs to a user
        """
        return [g.name for g in obj.groups.all()]
    
    def get_permissions(self, obj):
        """
            Returns all permission codename assigned directly or via roles
        """
        user_perms = Permission.objects.filter(user=obj).order_by().values_list("codename", flat=True)
        group_perms = Permission.objects.filter(group__user=obj).order_by().values_list("codename", flat=True)
        combined = user_perms.union(group_perms)
        return list(combined)
    
class AdminUserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [ "id", "email", "first_name", "last_name", "is_active", "roles", "permissions" ]
        
    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_permissions(self, obj):
        return sorted(list(obj.get_all_permissions()))