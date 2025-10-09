from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

from .models import Role
from .serializers import RoleSerializer, PermissionSerializer

# Create your views here.

User = get_user_model()

class RoleViewSet(viewsets.ModelViewSet):
    """
        CRUD API for Roles
    """
    queryset = Role.objects.all().order_by("name")
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
class PermissionListViewSet(viewsets.ModelViewSet):
    """
        List all available permission in the system
    """
    queryset = Permission.objects.all().order_by("content_type")
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
from rest_framework.decorators import action

class UserRoleViewSet(viewsets.ViewSet):
    """
    Assign and remove roles to users
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def assign_role(self, request, pk=None):
        """
        Assign a role to a user (POST /api/roles/user/<user_id>/assign_role/)
        body: {"role_id": 2}
        """
        try:
            user = User.objects.get(pk=pk)
            role_id = request.data.get("role_id")
            role = Role.objects.get(pk=role_id)
            user.groups.add(role)
            return Response({"message": f"Role '{role.name}' assigned to {user.email}."})
        except (User.DoesNotExist, Role.DoesNotExist):
            return Response({"error": "Invalid user or role ID."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def remove_role(self, request, pk=None):
        """
        Remove a role from a user (POST /api/roles/user/<user_id>/remove_role/)
        body: {"role_id": 2}
        """
        try:
            user = User.objects.get(pk=pk)
            role_id = request.data.get("role_id")
            role = Role.objects.get(pk=role_id)
            user.groups.remove(role)
            return Response({"message": f"Role '{role.name}' removed from {user.email}."})
        except (User.DoesNotExist, Role.DoesNotExist):
            return Response({"error": "Invalid user or role ID."}, status=status.HTTP_400_BAD_REQUEST)

