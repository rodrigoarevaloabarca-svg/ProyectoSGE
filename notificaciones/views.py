"""
APP: notificaciones
ARCHIVO: views.py
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings as django_settings
from django.db.models import Q

from .models import Notificacion, EnvioMasivo
from usuarios.models import Usuario


# ── Helpers de permisos ───────────────────────────────────────────────────────

def _puede_enviar(user):
    return True  # Todos los usuarios pueden enviar (alumnos/apoderados solo al admin)

def _solo_puede_escribir_al_admin(user):
    """Alumnos y apoderados solo pueden escribir al administrador."""
    return user.rol in ('alumno', 'apoderado')


# ── BANDEJA DE ENTRADA ────────────────────────────────────────────────────────

@login_required
def bandeja(request):
    """Lista todas las notificaciones recibidas por el usuario."""
    notifs      = Notificacion.objects.filter(destinatario=request.user).select_related('remitente')
    no_leidas   = notifs.filter(leida=False).count()
    leidas      = notifs.filter(leida=True)
    sin_leer    = notifs.filter(leida=False)

    return render(request, 'notificaciones/bandeja.html', {
        'notifs':    notifs,
        'sin_leer':  sin_leer,
        'leidas':    leidas,
        'no_leidas': no_leidas,
        'breadcrumbs': [
            {'label': 'Notificaciones', 'url': ''},
        ],
    })


@login_required
def ver_notificacion(request, pk):
    """Ver el detalle de una notificación y marcarla como leída."""
    notif = get_object_or_404(Notificacion, pk=pk, destinatario=request.user)
    notif.marcar_leida()

    return render(request, 'notificaciones/ver.html', {
        'notif': notif,
        'breadcrumbs': [
            {'label': 'Notificaciones', 'url': reverse('notificaciones:bandeja')},
            {'label': notif.titulo,     'url': ''},
        ],
    })


@login_required
def marcar_todas_leidas(request):
    """Marca todas las notificaciones del usuario como leídas."""
    Notificacion.objects.filter(
        destinatario=request.user, leida=False
    ).update(leida=True, fecha_leida=timezone.now())
    messages.success(request, 'Todas las notificaciones marcadas como leídas.')
    return redirect('notificaciones:bandeja')


# ── ENVIADAS ──────────────────────────────────────────────────────────────────

@login_required
def enviadas(request):
    """Historial de notificaciones enviadas por el usuario."""

    individuales = Notificacion.objects.filter(
        remitente=request.user
    ).exclude(envio_masivo__isnull=False).select_related('destinatario')

    masivos = EnvioMasivo.objects.filter(remitente=request.user)

    return render(request, 'notificaciones/enviadas.html', {
        'individuales': individuales,
        'masivos':      masivos,
        'breadcrumbs': [
            {'label': 'Notificaciones', 'url': reverse('notificaciones:bandeja')},
            {'label': 'Enviadas',       'url': ''},
        ],
    })


# ── REDACTAR MENSAJE INDIVIDUAL ───────────────────────────────────────────────

@login_required
def redactar(request):
    """Enviar notificación individual a un usuario."""
    user = request.user
    solo_admin = _solo_puede_escribir_al_admin(user)

    # Construir lista de destinatarios según rol
    if solo_admin:
        # Alumno / apoderado: solo pueden escribir al admin
        admin = Usuario.objects.filter(rol='admin', is_active=True).first()
        destinatarios = Usuario.objects.filter(rol='admin', is_active=True)
    elif user.es_admin:
        destinatarios = Usuario.objects.filter(
            is_active=True
        ).exclude(pk=user.pk).order_by('rol', 'last_name')
        admin = None
    elif user.es_profesor:
        from alumnos.models import Alumno
        alumnos_ids = Alumno.objects.filter(
            curso__asignaturas__profesor=user.perfil_profesor,
            activo=True
        ).values_list('apoderado__usuario', flat=True).distinct()
        destinatarios = Usuario.objects.filter(
            pk__in=alumnos_ids, is_active=True
        ).order_by('last_name')
        admin = None
    else:
        destinatarios = Usuario.objects.none()
        admin = None

    if request.method == 'POST':
        titulo       = request.POST.get('titulo', '').strip()
        mensaje      = request.POST.get('mensaje', '').strip()
        enviar_email = request.POST.get('enviar_email') == 'on'

        # Para alumnos/apoderados el destinatario siempre es el admin
        if solo_admin:
            destinatario = admin
            if not destinatario:
                messages.error(request, 'No hay un administrador disponible para recibir mensajes.')
                return redirect('notificaciones:bandeja')
        else:
            destinatario_id = request.POST.get('destinatario')
            if not destinatario_id:
                messages.error(request, 'Selecciona un destinatario.')
                return redirect('notificaciones:redactar')
            destinatario = get_object_or_404(Usuario, pk=destinatario_id)

        if not titulo or not mensaje:
            messages.error(request, 'Completa todos los campos.')
        else:
            Notificacion.objects.create(
                remitente=user,
                destinatario=destinatario,
                titulo=titulo,
                mensaje=mensaje,
                tipo='mensaje',
                enviada_por_email=enviar_email,
            )
            if enviar_email and destinatario.email:
                _enviar_email_notificacion(
                    destinatario=destinatario,
                    remitente=user,
                    titulo=titulo,
                    mensaje=mensaje,
                )
            messages.success(request, f'Mensaje enviado a {destinatario.get_full_name()}.')
            return redirect('notificaciones:bandeja')

    return render(request, 'notificaciones/redactar.html', {
        'destinatarios': destinatarios,
        'solo_admin':    solo_admin,
        'breadcrumbs': [
            {'label': 'Notificaciones', 'url': reverse('notificaciones:bandeja')},
            {'label': 'Redactar',       'url': ''},
        ],
    })


# ── ENVÍO MASIVO (solo admin) ─────────────────────────────────────────────────

@login_required
def envio_masivo(request):
    """Envío masivo a todos los apoderados y/o profesores."""
    if not request.user.es_admin:
        return redirect('notificaciones:bandeja')

    from cursos.models import Curso
    cursos = Curso.objects.filter(activo=True).order_by('nivel', 'grado', 'letra')

    if request.method == 'POST':
        titulo       = request.POST.get('titulo', '').strip()
        mensaje      = request.POST.get('mensaje', '').strip()
        destino      = request.POST.get('destino', '')
        curso_id     = request.POST.get('curso')
        enviar_email = request.POST.get('enviar_email') == 'on'

        if not titulo or not mensaje or not destino:
            messages.error(request, 'Completa todos los campos.')
        else:
            destinatarios = _resolver_destinatarios(destino, curso_id)

            if not destinatarios.exists():
                messages.warning(request, 'No se encontraron destinatarios para ese grupo.')
            else:
                # Crear registro del envío masivo
                curso_obj = None
                if curso_id and destino == 'curso_apoderados':
                    from cursos.models import Curso as CursoModel
                    curso_obj = CursoModel.objects.filter(pk=curso_id).first()

                envio = EnvioMasivo.objects.create(
                    remitente=request.user,
                    titulo=titulo,
                    mensaje=mensaje,
                    destino=destino,
                    curso=curso_obj,
                    total_enviados=destinatarios.count(),
                    enviado_email=enviar_email,
                )

                # Crear notificación individual para cada destinatario
                notifs = [
                    Notificacion(
                        remitente=request.user,
                        destinatario=dest,
                        titulo=titulo,
                        mensaje=mensaje,
                        tipo='masivo',
                        enviada_por_email=enviar_email,
                        envio_masivo=envio,
                    )
                    for dest in destinatarios
                ]
                Notificacion.objects.bulk_create(notifs)

                # Enviar emails si se solicitó
                if enviar_email:
                    _enviar_emails_masivo(
                        destinatarios=destinatarios,
                        remitente=request.user,
                        titulo=titulo,
                        mensaje=mensaje,
                    )

                messages.success(
                    request,
                    f'Mensaje enviado a {destinatarios.count()} destinatarios'
                    + (' + email' if enviar_email else '') + '.'
                )
                return redirect('notificaciones:enviadas')

    DESTINOS = [
        ('todos_apoderados',  'Todos los apoderados'),
        ('todos_profesores',  'Todos los profesores'),
        ('todos_alumnos',     'Todos los alumnos'),
        ('todos',             'Apoderados y profesores'),
        ('todos_comunidad',   'Toda la comunidad'),
        ('curso_apoderados',  'Apoderados de un curso'),
        ('curso_alumnos',     'Alumnos de un curso'),
        ('curso_todos',       'Alumnos + apoderados de un curso'),
    ]

    return render(request, 'notificaciones/masivo.html', {
        'cursos':        cursos,
        'view_destinos': DESTINOS,
        'breadcrumbs': [
            {'label': 'Notificaciones', 'url': reverse('notificaciones:bandeja')},
            {'label': 'Envío masivo',   'url': ''},
        ],
    })


# ── HELPERS PRIVADOS ──────────────────────────────────────────────────────────

def _resolver_destinatarios(destino, curso_id=None):
    """Retorna QuerySet de usuarios según el destino elegido."""
    from alumnos.models import Alumno

    if destino == 'todos_apoderados':
        return Usuario.objects.filter(rol='apoderado', is_active=True)

    elif destino == 'todos_profesores':
        return Usuario.objects.filter(rol='profesor', is_active=True)

    elif destino == 'todos_alumnos':
        return Usuario.objects.filter(rol='alumno', is_active=True)

    elif destino == 'todos':
        return Usuario.objects.filter(rol__in=['apoderado', 'profesor'], is_active=True)

    elif destino == 'todos_comunidad':
        return Usuario.objects.filter(
            rol__in=['apoderado', 'profesor', 'alumno'], is_active=True
        )

    elif destino == 'curso_apoderados' and curso_id:
        apoderados_ids = Alumno.objects.filter(
            curso_id=curso_id, activo=True, apoderado__isnull=False
        ).values_list('apoderado__usuario', flat=True).distinct()
        return Usuario.objects.filter(pk__in=apoderados_ids, is_active=True)

    elif destino == 'curso_alumnos' and curso_id:
        alumnos_ids = Alumno.objects.filter(
            curso_id=curso_id, activo=True
        ).values_list('usuario', flat=True).distinct()
        return Usuario.objects.filter(pk__in=alumnos_ids, is_active=True)

    elif destino == 'curso_todos' and curso_id:
        alumnos_ids = list(Alumno.objects.filter(
            curso_id=curso_id, activo=True
        ).values_list('usuario', flat=True).distinct())
        apoderados_ids = list(Alumno.objects.filter(
            curso_id=curso_id, activo=True, apoderado__isnull=False
        ).values_list('apoderado__usuario', flat=True).distinct())
        return Usuario.objects.filter(
            pk__in=alumnos_ids + apoderados_ids, is_active=True
        ).distinct()

    return Usuario.objects.none()


def _enviar_email_notificacion(destinatario, remitente, titulo, mensaje):
    """Envía un email individual de notificación."""
    if not destinatario.email:
        return

    asunto   = f'[SGE] {titulo}'
    cuerpo   = (
        f'Estimado/a {destinatario.get_full_name()},\n\n'
        f'{mensaje}\n\n'
        f'— {remitente.get_full_name()}\n'
        f'Sistema de Gestión Escolar (SGE)'
    )
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px;border:1px solid #e2e8f0;border-radius:12px">
        <div style="background:#197fe6;padding:16px 24px;border-radius:8px 8px 0 0;margin:-24px -24px 24px">
            <h2 style="color:white;margin:0;font-size:18px">🏫 SGE — Notificación</h2>
        </div>
        <p style="color:#6b7fa3;font-size:13px;margin-bottom:4px">Estimado/a</p>
        <h3 style="color:#0d1b2a;margin:0 0 16px">{destinatario.get_full_name()}</h3>
        <div style="background:#f8fafc;border-left:4px solid #197fe6;padding:16px;border-radius:4px;margin-bottom:24px">
            <h4 style="margin:0 0 8px;color:#0d1b2a">{titulo}</h4>
            <p style="margin:0;color:#374151;line-height:1.6">{mensaje}</p>
        </div>
        <p style="color:#6b7fa3;font-size:12px;border-top:1px solid #e2e8f0;padding-top:16px;margin:0">
            Enviado por <strong>{remitente.get_full_name()}</strong> · Sistema de Gestión Escolar
        </p>
    </div>
    """
    try:
        email = EmailMultiAlternatives(
            subject=asunto,
            body=cuerpo,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[destinatario.email],
        )
        email.attach_alternative(html, 'text/html')
        email.send(fail_silently=True)
    except Exception:
        pass


def _enviar_emails_masivo(destinatarios, remitente, titulo, mensaje):
    """Envía emails a múltiples destinatarios."""
    for dest in destinatarios:
        if dest.email:
            _enviar_email_notificacion(dest, remitente, titulo, mensaje)


# ── Función pública para usar desde otras apps (signals) ─────────────────────

def crear_notificacion(remitente, destinatario, titulo, mensaje, enviar_email=False):
    """
    Función auxiliar para crear notificaciones desde otras partes del sistema.
    Ejemplo de uso desde anotaciones/views.py:
        from notificaciones.views import crear_notificacion
        crear_notificacion(request.user, apoderado.usuario,
                          'Nueva anotación', f'...')
    """
    notif = Notificacion.objects.create(
        remitente=remitente,
        destinatario=destinatario,
        titulo=titulo,
        mensaje=mensaje,
        enviada_por_email=enviar_email,
    )
    if enviar_email and destinatario.email:
        _enviar_email_notificacion(destinatario, remitente, titulo, mensaje)
    return notif
