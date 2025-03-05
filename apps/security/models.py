from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
import os

def user_avatar_path(instance, filename):
    """Define la ruta donde se guardarán los avatares de usuario"""
    extension = filename.split('.')[-1]
    return f'users/avatars/{instance.id}.{extension}'

class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende el AbstractUser de Django 
    con campos adicionales específicos para la aplicación de fotografía
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('correo electrónico'), unique=True)
    phone = models.CharField(_('teléfono'), max_length=15, blank=True, null=True)
    avatar = models.ImageField(_('avatar'), upload_to=user_avatar_path, blank=True, null=True)
    bio = models.TextField(_('biografía'), blank=True, null=True)
    
    # Campos para seguimiento y estadísticas
    sessions_created = models.PositiveIntegerField(_('sesiones creadas'), default=0)
    completed_sessions = models.PositiveIntegerField(_('sesiones completadas'), default=0)
    last_session_date = models.DateTimeField(_('fecha última sesión'), blank=True, null=True)
    
    # Configuraciones de usuario
    preferred_countdown = models.IntegerField(_('cuenta regresiva preferida'), default=3)
    preferred_interval = models.IntegerField(_('intervalo preferido'), default=5)
    
    # Campos para gestión de fechas
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)
    
    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['-date_joined']
    
    def __str__(self):
        """Representación en string del usuario"""
        return self.get_full_name() or self.username or self.email
    
    def get_full_name(self):
        """Devuelve el nombre completo del usuario"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else None
    
    def increment_session_count(self):
        """Incrementa el contador de sesiones creadas"""
        self.sessions_created += 1
        self.save(update_fields=['sessions_created'])
    
    def complete_session(self):
        """Registra una sesión completada"""
        self.completed_sessions += 1
        self.last_session_date = timezone.now()
        self.save(update_fields=['completed_sessions', 'last_session_date'])
    
    def get_session_statistics(self):
        """Obtiene estadísticas sobre las sesiones del usuario"""
        return {
            'total': self.sessions_created,
            'completed': self.completed_sessions,
            'completion_rate': round((self.completed_sessions / self.sessions_created * 100) 
                                     if self.sessions_created > 0 else 0, 2),
            'last_session': self.last_session_date
        }