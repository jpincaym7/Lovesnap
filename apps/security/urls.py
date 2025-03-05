from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.security.views.api_auth import AuthView
from apps.security.viewsets.auth_view import AuthViewSet, UserViewSet

app_name = "security"

# Configurar router para los viewsets
router = DefaultRouter()
router.register(r'users', AuthViewSet, basename='user')
router.register(r'profile', UserViewSet, basename='profile')

# Definir patrones de URL
urlpatterns = [
    path('', include(router.urls)),
    path("auth/", AuthView.as_view(), name="auth-api")
]