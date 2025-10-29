
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import GoogleVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


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
    
    # Documentation using Swagger
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    
    # Paga endpoints urls
    path("api/payments/", include("apps.paga_payments.urls")),
    
    # Projects and Tasks endpoints
    path("api/", include("apps.projects.urls"))
]
