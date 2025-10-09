from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet

router = DefaultRouter()
router.register(r"users", AdminUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
