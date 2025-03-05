from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from apps.security.models import User
from apps.custom_templates.models import PhotoTemplate
from apps.core.utils import generate_access_code

class PhotoSession(models.Model):
    """Modelo para las sesiones de fotos"""
    # Constantes para estados de sesión
    STATUS_CREATED = 'created'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (STATUS_CREATED, _('Creada')),
        (STATUS_IN_PROGRESS, _('En progreso')),
        (STATUS_COMPLETED, _('Completada')),
        (STATUS_EXPIRED, _('Expirada')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        verbose_name=_('usuario'),
        on_delete=models.CASCADE, 
        related_name='photo_sessions',
        blank=True, 
        null=True
    )
    template = models.ForeignKey(
        PhotoTemplate, 
        verbose_name=_('plantilla'),
        on_delete=models.SET_NULL, 
        related_name='sessions',
        null=True
    )
    title = models.CharField(_('título'), max_length=100, blank=True, null=True)
    access_code = models.CharField(_('código de acceso'), max_length=8, unique=True, blank=True, null=True)
    status = models.CharField(
        _('estado'),
        max_length=15, 
        choices=STATUS_CHOICES, 
        default=STATUS_CREATED
    )
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    completed_at = models.DateTimeField(_('fecha de finalización'), blank=True, null=True)
    expires_at = models.DateTimeField(_('fecha de expiración'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('sesión de fotos')
        verbose_name_plural = _('sesiones de fotos')
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para gestionar la generación de código y fechas"""
        if not self.access_code:
            self.access_code = generate_access_code()
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
            
        # Si es una sesión nueva, incrementa el contador del usuario
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Actualiza estadísticas del usuario si existe
        if is_new and self.user:
            self.user.increment_session_count()
    
    def __str__(self):
        """Representación en string de la sesión"""
        return f"{self.title or 'Sesión'} ({self.access_code})"
    
    @property
    def is_expired(self):
        """Verifica si la sesión ha expirado"""
        return self.expires_at < timezone.now()
    
    def mark_completed(self):
        """Marca la sesión como completada y actualiza estadísticas del usuario"""
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save()
        
        if self.user:
            self.user.complete_session()
    
    def mark_in_progress(self):
        """Marca la sesión como en progreso"""
        self.status = self.STATUS_IN_PROGRESS
        self.save()
    
    def extend_expiration(self, hours=24):
        """Extiende el tiempo de expiración de la sesión"""
        self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        self.save()

class SessionSettings(models.Model):
    """Configuración para la sesión de fotos"""
    session = models.OneToOneField(
        PhotoSession, 
        verbose_name=_('sesión'),
        related_name='settings', 
        on_delete=models.CASCADE
    )
    num_photos = models.IntegerField(_('número de fotos'), default=4)
    countdown_seconds = models.IntegerField(_('segundos de cuenta atrás'), default=3)
    interval_seconds = models.IntegerField(_('segundos entre fotos'), default=5)
    allow_retake = models.BooleanField(_('permitir repetir'), default=True)
    
    class Meta:
        verbose_name = _('configuración de sesión')
        verbose_name_plural = _('configuraciones de sesiones')
    
    def __str__(self):
        return f"Configuración para {self.session}"
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para usar las preferencias del usuario si no hay valores específicos"""
        is_new = self.pk is None
        
        if is_new and self.session.user:
            # Si es una configuración nueva, usar preferencias de usuario
            if not self.countdown_seconds:
                self.countdown_seconds = self.session.user.preferred_countdown
            if not self.interval_seconds:
                self.interval_seconds = self.session.user.preferred_interval
                
        super().save(*args, **kwargs)