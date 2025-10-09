from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, PermissionListViewSet, UserRoleViewSet

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"permissions", PermissionListViewSet, basename="permission")

user_role = DefaultRouter()
user_role.register(r"user", UserRoleViewSet, basename="user-role")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(user_role.urls)),
]
