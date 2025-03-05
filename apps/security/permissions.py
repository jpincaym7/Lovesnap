from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite a los propietarios del objeto editar,
    mientras que usuarios no autenticados sólo pueden ver.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permitir métodos seguros (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Permitir edición solo si el usuario es propietario del objeto
        # o si es administrador
        return obj.id == request.user.id or request.user.is_staff