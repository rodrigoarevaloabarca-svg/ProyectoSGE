"""dashboard/views.py"""
import json
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from historial.models import HistorialCambio
from SGE.ia_utils import chatbot_consulta

from .forms import ContactoForm


def contacto(request):
    form = ContactoForm()

    if request.method == 'POST':
        ultimo_envio = request.session.get('ultimo_envio_contacto', 0)
        ahora = time.time()

        if ahora - ultimo_envio < 60:
            tiempo_restante = int(60 - (ahora - ultimo_envio))
            messages.error(request, f'Por favor, espera {tiempo_restante} segundos antes de enviar otro mensaje.')
            return render(request, 'complementos_login/contacto.html', {'form': form})

        form = ContactoForm(request.POST)
        if form.is_valid():
            nombre  = form.cleaned_data['nombre']
            email   = form.cleaned_data['email']
            rol     = form.cleaned_data['rol']
            asunto  = form.cleaned_data['asunto']
            mensaje = form.cleaned_data['mensaje']

            cuerpo = f"""
            Nuevo mensaje desde el formulario de contacto SGE
            --------------------------------------------------
            Nombre:  {nombre}
            Email:   {email}
            Rol:     {rol}
            Asunto:  {asunto}

            Mensaje:
            {mensaje}
                        """

            send_mail(
                subject=f'[SGE Contacto] {asunto}',
                message=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACTO_EMAIL_ADMIN],
                fail_silently=False,
            )

            request.session['ultimo_envio_contacto'] = ahora
            messages.success(request, '¡Mensaje enviado correctamente! Te responderemos en menos de 24 horas.')
            form = ContactoForm()

    return render(request, 'complementos_login/contacto.html', {'form': form})


# ── Helpers por rol ───────────────────────────────────────────────────────────

def _dashboard_admin(request):
    from alumnos.models import Alumno
    from anotaciones.models import Anotacion
    from asignaturas.models import Asignatura
    from cursos.models import Curso
    from notificaciones.models import EnvioMasivo, Notificacion
    from profesores.models import Profesor

    user = request.user
    todas_notifs = Notificacion.objects.filter(
        destinatario=user
    ).select_related('remitente').order_by('-fecha_envio')

    context = {
        'total_alumnos':      Alumno.objects.count(),
        'total_profesores':   Profesor.objects.filter(activo=True).count(),
        'total_cursos':       Curso.objects.count(),
        'total_asignaturas':  Asignatura.objects.count(),
        'cursos':             Curso.objects.select_related('nivel', 'profesor_jefe__usuario').all(),
        'ultimas_anotaciones': Anotacion.objects.select_related(
            'alumno__usuario', 'creado_por'
        ).order_by('-fecha')[:5],
        'notifs_recibidas':   todas_notifs[:5],
        'ultimos_masivos':    EnvioMasivo.objects.filter(remitente=user).order_by('-fecha_envio')[:3],
        'total_enviadas':     Notificacion.objects.filter(remitente=user).count(),
        'sin_leer_sistema':   Notificacion.objects.filter(leida=False).count(),
        'notif_no_leidas':    todas_notifs.filter(leida=False).count(),
        'ultimos_cambios':    HistorialCambio.objects.select_related('modificado_por').order_by('-fecha')[:5],
    }
    return render(request, 'dashboard/admin.html', context)


def _dashboard_profesor(request):
    from alumnos.models import Alumno
    from asignaturas.models import Asignatura
    from cursos.models import Curso
    from notificaciones.models import Notificacion

    user = request.user
    try:
        profesor = user.perfil_profesor
    except Exception:
        return render(request, 'dashboard/profesor.html', {
            'profesor': None, 'asignaturas': [], 'mis_cursos': [],
            'total_alumnos': 0, 'notifs_recibidas': [], 'notif_no_leidas': 0,
        })

    asignaturas = Asignatura.objects.filter(profesor=profesor).select_related('curso')
    mis_cursos  = Curso.objects.filter(asignaturas__profesor=profesor).distinct()
    notifs_qs   = Notificacion.objects.filter(destinatario=user).select_related('remitente').order_by('-fecha_envio')

    context = {
        'profesor':              profesor,
        'asignaturas':           asignaturas,
        'mis_cursos':            mis_cursos,
        'total_alumnos':         Alumno.objects.filter(curso__in=mis_cursos).count(),
        'notifs_recibidas':      notifs_qs[:5],
        'notif_no_leidas':       notifs_qs.filter(leida=False).count(),
        'alumnos_con_apoderado': Alumno.objects.filter(
            curso__in=mis_cursos, activo=True, apoderado__isnull=False
        ).select_related('usuario', 'curso', 'apoderado__usuario').order_by(
            'curso__grado', 'curso__letra', 'usuario__last_name'
        ),
    }
    return render(request, 'dashboard/profesor.html', context)


def _dashboard_apoderado(request):
    from asistencia.models import RegistroAsistencia
    from notificaciones.models import Notificacion

    user = request.user
    try:
        apoderado = user.perfil_apoderado
    except Exception:
        return render(request, 'dashboard/apoderado.html', {
            'apoderado': None, 'datos_pupilos': [],
            'notifs_recibidas': [], 'notif_no_leidas': 0,
        })

    datos_pupilos = []
    for alumno in apoderado.pupilos.select_related('usuario', 'curso').all():
        ausencias = RegistroAsistencia.objects.filter(
            alumno=alumno, estado__in=['ausente', 'atrasado', 'justificado']
        ).select_related('asignatura').order_by('-fecha')[:10]
        datos_pupilos.append({
            'alumno':                alumno,
            'promedio_general':      alumno.get_promedio_general(),
            'porcentaje_asistencia': alumno.get_porcentaje_asistencia(),
            'anotaciones_recientes': alumno.anotaciones.select_related('creado_por').order_by('-fecha')[:3],
            'ausencias_recientes':   ausencias,
        })

    notifs_qs = Notificacion.objects.filter(destinatario=user).select_related('remitente').order_by('-fecha_envio')
    context = {
        'apoderado':        apoderado,
        'datos_pupilos':    datos_pupilos,
        'notifs_recibidas': notifs_qs[:5],
        'notif_no_leidas':  notifs_qs.filter(leida=False).count(),
    }
    return render(request, 'dashboard/apoderado.html', context)


def _dashboard_alumno(request):
    from anotaciones.models import Anotacion
    from asistencia.models import RegistroAsistencia
    from notas.models import PromedioAsignatura
    from notificaciones.models import Notificacion

    user = request.user
    try:
        alumno = user.perfil_alumno
    except Exception:
        return render(request, 'dashboard/alumno.html', {'alumno': None})

    promedios     = PromedioAsignatura.objects.filter(alumno=alumno).select_related(
        'asignatura', 'asignatura__profesor'
    ).order_by('asignatura__nombre')
    promedios_vals = [p.promedio for p in promedios if p.promedio is not None]
    promedio_general = round(sum(promedios_vals) / len(promedios_vals), 1) if promedios_vals else None

    asistencia_qs = RegistroAsistencia.objects.filter(alumno=alumno)
    total_dias    = asistencia_qs.count()
    dias_presentes = asistencia_qs.filter(estado='presente').count()
    porcentaje_asistencia = round((dias_presentes / total_dias) * 100, 1) if total_dias > 0 else None

    notifs_qs = Notificacion.objects.filter(destinatario=user).select_related('remitente').order_by('-fecha_envio')
    context = {
        'alumno':                alumno,
        'promedios':             promedios,
        'promedio_general':      promedio_general,
        'porcentaje_asistencia': porcentaje_asistencia,
        'anotaciones':           Anotacion.objects.filter(alumno=alumno).select_related('creado_por').order_by('-fecha')[:5],
        'notifs_recibidas':      notifs_qs[:5],
        'notif_no_leidas':       notifs_qs.filter(leida=False).count(),
    }
    return render(request, 'dashboard/alumno.html', context)


# ── Vistas públicas ───────────────────────────────────────────────────────────

@login_required
def inicio(request):
    user = request.user
    if user.rol == 'admin' or user.is_superuser:
        return _dashboard_admin(request)
    elif user.rol == 'profesor':
        return _dashboard_profesor(request)
    elif user.rol == 'apoderado':
        return _dashboard_apoderado(request)
    elif user.rol == 'alumno':
        return _dashboard_alumno(request)
    return render(request, 'dashboard/sin_rol.html', {})


@login_required
@require_POST
def chatbot_ia(request):
    if not (request.user.es_admin or request.user.es_profesor):
        return JsonResponse({'error': 'Sin permiso'}, status=403)

    try:
        datos = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Formato de solicitud inválido'}, status=400)

    pregunta     = datos.get('pregunta', '').strip()
    historial_raw = datos.get('historial', [])

    if not pregunta:
        return JsonResponse({'error': 'Pregunta vacía'}, status=400)
    if len(pregunta) > 1000:
        return JsonResponse({'error': 'Pregunta demasiado larga (máx. 1000 caracteres)'}, status=400)

    historial = [
        {'role': m['role'], 'content': str(m['content'])[:2000]}
        for m in historial_raw
        if isinstance(m, dict)
        and m.get('role') in ('user', 'assistant')
        and isinstance(m.get('content'), str)
    ][-10:]

    import logging
    logger = logging.getLogger(__name__)
    try:
        respuesta = chatbot_consulta(pregunta, request.user, historial)
        return JsonResponse({'respuesta': respuesta})
    except Exception as e:
        logger.error("Error en chatbot endpoint para usuario %s: %s", request.user.pk, e, exc_info=True)
        return JsonResponse({'error': 'Error al conectar con la IA'}, status=500)
