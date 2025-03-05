from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
import os
from apps.custom_sessions.models import PhotoSession
from apps.core.utils import safe_delete_file

def session_directory_path(instance, filename):
    """Define la ruta donde se guardarán los archivos de sesión"""
    return f'sessions/{instance.session.id}/{filename}'

def photo_directory_path(instance, filename):
    """Define la ruta donde se guardarán las fotos individuales"""
    return f'sessions/{instance.session.id}/photos/{filename}'

class IndividualPhoto(models.Model):
    """Modelo para cada foto individual tomada en la sesión"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        PhotoSession, 
        verbose_name=_('sesión'),
        related_name='photos', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(_('imagen'), upload_to=photo_directory_path)
    order = models.IntegerField(_('orden'), default=0)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('foto individual')
        verbose_name_plural = _('fotos individuales')
        ordering = ['session', 'order']
    
    def __str__(self):
        return f"Foto {self.order} - {self.session}"
    
    def delete(self, *args, **kwargs):
        """Sobrescribe delete para eliminar también el archivo físico"""
        if self.image:
            safe_delete_file(self.image.path)
        super().delete(*args, **kwargs)

class CompositePhoto(models.Model):
    """Modelo para la foto compuesta final (unión de varias fotos)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        PhotoSession, 
        verbose_name=_('sesión'),
        related_name='composites', 
        on_delete=models.CASCADE
    )
    image = models.ImageField(_('imagen'), upload_to=session_directory_path)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('foto compuesta')
        verbose_name_plural = _('fotos compuestas')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Composite de {self.session}"
    
    def delete(self, *args, **kwargs):
        """Sobrescribe delete para eliminar también el archivo físico"""
        if self.image:
            safe_delete_file(self.image.path)
        super().delete(*args, **kwargs)