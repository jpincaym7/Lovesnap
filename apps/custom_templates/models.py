from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.security.models import User

class PhotoTemplate(models.Model):
    """Modelo para las plantillas de diseño para las fotos finales"""
    name = models.CharField(_('nombre'), max_length=100)
    description = models.TextField(_('descripción'), blank=True, null=True)
    image = models.ImageField(_('imagen'), upload_to='templates/')
    max_photos = models.IntegerField(_('máximo de fotos'), default=4)
    is_active = models.BooleanField(_('activa'), default=True)
    created_by = models.ForeignKey(
        User, 
        verbose_name=_('creado por'),
        on_delete=models.SET_NULL, 
        related_name='created_templates',
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('plantilla de foto')
        verbose_name_plural = _('plantillas de foto')
        ordering = ['-created_at']

    def __str__(self):
        return self.name