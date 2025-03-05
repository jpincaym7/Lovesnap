from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _

from apps.security.models import User
from apps.security.serializers.auth_serial import (
    UserRegistrationSerializer,
    UserLoginSerializer, 
    UserProfileSerializer
)
from apps.security.permissions import IsOwnerOrReadOnly
from django.contrib.auth import login

class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet para manejar la autenticación de usuarios:
    registro, login y logout.
    """
    queryset = User.objects.all()
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Endpoint para registrar un nuevo usuario.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Crear token de autenticación para el nuevo usuario
            token, created = Token.objects.get_or_create(user=user)
            # Devolver respuesta con datos de usuario y token
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        Endpoint para iniciar sesión.
        Acepta login como email o username.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Crear o recuperar token de autenticación
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            # Devolver respuesta con datos de usuario y token
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """
        Endpoint para cerrar sesión.
        Elimina el token de autenticación del usuario.
        """
        try:
            # Eliminar token de autenticación
            request.user.auth_token.delete()
            # Cerrar sesión en Django
            logout(request)
            return Response({"detail": _("Sesión cerrada exitosamente.")}, 
                           status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": _("Error al cerrar sesión.")}, 
                           status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar perfiles de usuario.
    Proporciona CRUD completo para usuarios.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        """
        Determina el serializer a utilizar según la acción.
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        """
        Establece permisos dinámicos según la acción.
        """
        if self.action in ['create', 'list']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filtra el queryset según el usuario y la acción.
        Los administradores pueden ver todos los usuarios.
        Los usuarios normales solo pueden ver sus propios datos.
        """
        if self.action == 'list' and not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener el perfil del usuario autenticado.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """
        Endpoint para actualizar datos de perfil del usuario autenticado.
        """
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        Endpoint para cambiar contraseña del usuario autenticado.
        """
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validar datos de entrada
        if not current_password or not new_password or not confirm_password:
            return Response(
                {"detail": _("Todos los campos son requeridos.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar contraseña actual
        if not user.check_password(current_password):
            return Response(
                {"detail": _("La contraseña actual es incorrecta.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que las nuevas contraseñas coincidan
        if new_password != confirm_password:
            return Response(
                {"detail": _("Las nuevas contraseñas no coinciden.")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        # Actualizar token para forzar re-login
        user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "detail": _("Contraseña actualizada exitosamente."),
            "token": token.key
        })