from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import ProjectViewSet, TaskViewSet

from apps.request.views import RequestViewSet

# Create a router for projects
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='projects')

# Create a nested router for tasks under projects
projects_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
projects_router.register(r'tasks', TaskViewSet, basename='project-tasks')

# Registering the request url
router.register(r'requests', RequestViewSet, basename='request')

urlpatterns = router.urls + projects_router.urls
