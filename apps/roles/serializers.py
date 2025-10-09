from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import Role

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "codename", "name", "content_type"]
        
class RoleSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = ["id", "name", "description", "permission", "permission_ids"]
        
    def create(self, validated_data):
        """
            Method used to create roles
        """
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        if permission_ids:
            role.permissions.set(permission_ids)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop("permission_ids", None)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        return instance