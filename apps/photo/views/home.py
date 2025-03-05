from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from apps.custom_sessions.models import PhotoSession
from apps.photo.models import IndividualPhoto, CompositePhoto

@login_required
def home_view(request):
    """
    Vista para la página de inicio con estadísticas y datos de sesiones
    """
    # Obtener sesiones del usuario actual
    user_sessions = PhotoSession.objects.filter(user=request.user)
    
    # Estadísticas de álbumes (sesiones)
    total_sessions = user_sessions.count()
    
    # Contar fotos individuales
    total_memories = IndividualPhoto.objects.filter(session__user=request.user).count()
    
    # Obtener sesiones recientes con sus compuestos
    recent_sessions = user_sessions.prefetch_related('composites').order_by('-created_at')[:3]
    
    # Calcular uso de almacenamiento (simulado)
    # Esto es un ejemplo simple, podrías mejorarlo con cálculos más precisos
    total_file_size = sum(
        photo.image.size for session in recent_sessions 
        for photo in session.composites.all()
    )
    max_storage = 1024 * 1024 * 1024  # 1GB en bytes
    storage_used = min(round((total_file_size / max_storage) * 100, 2), 100)
    
    context = {
        'total_albums': total_sessions,
        'total_memories': total_memories,
        'storage_used': storage_used,
        'recent_albums': [
            {
                'name': session.name or f'Session {session.id}',
                'cover_image': session.composites.first().image.url if session.composites.exists() else None,
                'photo_count': session.photos.count(),
                'created_at': session.created_at
            } for session in recent_sessions
        ]
    }
    
    return render(request, 'sections/home.html', context)