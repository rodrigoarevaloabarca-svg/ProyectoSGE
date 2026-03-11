"""
APP: notificaciones
ARCHIVO: context_processors.py

Inyecta el contador de notificaciones no leídas en TODOS los templates.
Registrar en settings.py > TEMPLATES > OPTIONS > context_processors:
    'notificaciones.context_processors.notificaciones_no_leidas',
"""


def notificaciones_no_leidas(request):
    """Agrega `notif_count` al contexto global de todos los templates."""
    if request.user.is_authenticated:
        from .models import Notificacion
        count = Notificacion.objects.filter(
            destinatario=request.user,
            leida=False
        ).count()
        return {'notif_count': count}
    return {'notif_count': 0}
