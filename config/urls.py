"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import GoogleVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    
    # Implemented for url redirection using the backend
    path("api/auth/google/", include("allauth.socialaccount.urls")),
    
    # Google token verification endpoint
    path("api/auth/google/verify", GoogleVerifyView.as_view(), name="google-verify"),
    
    # Roles endpoints url:
    path("api/", include("apps.roles.urls")),
    
    # Users CRUD urls endpoints
    path("api/", include("apps.users.urls")),
]
