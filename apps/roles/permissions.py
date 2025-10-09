from rest_framework.permissions import BasePermission

def HasRole(allowed_roles):
    class _HasRole(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            if not user or not user.is_authenticated:
                return False
            if user.is_superuser:
                return True  # Superuser bypass
            user_roles = [g.name for g in user.groups.all()]
            return any(role in user_roles for role in allowed_roles)
    return _HasRole