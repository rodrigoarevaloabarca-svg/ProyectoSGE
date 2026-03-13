"""dashboard/views.py — con notificaciones integradas en todos los roles"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from historial.models import HistorialCambio


@login_required
def inicio(request):
    user = request.user
    from notificaciones.models import Notificacion

    # ── ADMIN ──────────────────────────────────────────────────────────────
    if user.rol == 'admin' or user.is_superuser:
        from alumnos.models import Alumno
        from profesores.models import Profesor
        from cursos.models import Curso
        from asignaturas.models import Asignatura
        from anotaciones.models import Anotacion
        from notificaciones.models import EnvioMasivo

        # 1. Obtenemos la consulta base (sin límite)
        todas_notifs_recibidas = Notificacion.objects.filter(
            destinatario=user
        ).select_related('remitente').order_by('-fecha_envio')

        # 2. Contamos las no leídas usando la consulta completa
        notif_no_leidas = todas_notifs_recibidas.filter(leida=False).count()

        # 3. Aplicamos el límite para mostrarlas en el dashboard
        notifs_recibidas = todas_notifs_recibidas[:5]

        # Últimos envíos masivos realizados
        ultimos_masivos = EnvioMasivo.objects.filter(
            remitente=user
        ).order_by('-fecha_envio')[:3]

        # Estadísticas globales de notificaciones del sistema
        total_enviadas_hoy = Notificacion.objects.filter(
            remitente=user
        ).count()
        sin_leer_sistema = Notificacion.objects.filter(leida=False).count()

        context = {
            'total_alumnos':      Alumno.objects.count(),
            'total_profesores':   Profesor.objects.filter(activo=True).count(),
            'total_cursos':       Curso.objects.count(),
            'total_asignaturas':  Asignatura.objects.count(),
            'cursos':             Curso.objects.select_related().all(),
            'ultimas_anotaciones': Anotacion.objects.select_related(
                'alumno__usuario', 'creado_por'
            ).order_by('-fecha')[:5],
            # Notificaciones
            'notifs_recibidas':   notifs_recibidas,
            'ultimos_masivos':    ultimos_masivos,
            'total_enviadas':     total_enviadas_hoy,
            'sin_leer_sistema':   sin_leer_sistema,
            'notif_no_leidas':    notif_no_leidas, # Variable ya calculada correctamente
            'ultimos_cambios': HistorialCambio.objects.select_related('modificado_por').order_by('-fecha')[:5],

        }
        return render(request, 'dashboard/admin.html', context)

    # ── PROFESOR ───────────────────────────────────────────────────────────
    elif user.rol == 'profesor':
        try:
            profesor = user.perfil_profesor
        except Exception:
            return render(request, 'dashboard/profesor.html', {
                'profesor': None, 'asignaturas': [], 'mis_cursos': [],
                'total_alumnos': 0, 'notifs_recibidas': [], 'notif_no_leidas': 0,
            })

        from asignaturas.models import Asignatura
        from cursos.models import Curso
        from alumnos.models import Alumno

        asignaturas = Asignatura.objects.filter(
            profesor=profesor
        ).select_related('curso')

        mis_cursos = Curso.objects.filter(
            asignaturas__profesor=profesor
        ).distinct()

        total_alumnos = Alumno.objects.filter(curso__in=mis_cursos).count()

        # Notificaciones recibidas del profesor
        notifs_recibidas = Notificacion.objects.filter(
            destinatario=user
        ).select_related('remitente').order_by('-fecha_envio')[:5]

        notif_no_leidas = Notificacion.objects.filter(
            destinatario=user, leida=False
        ).count()

        # Alumnos de sus cursos con sus apoderados (para envío rápido)
        alumnos_con_apoderado = Alumno.objects.filter(
            curso__in=mis_cursos, activo=True,
            apoderado__isnull=False
        ).select_related('usuario', 'curso', 'apoderado__usuario').order_by(
            'curso__grado', 'curso__letra', 'usuario__last_name'
        )

        context = {
            'profesor':               profesor,
            'asignaturas':            asignaturas,
            'mis_cursos':             mis_cursos,
            'total_alumnos':          total_alumnos,
            'notifs_recibidas':       notifs_recibidas,
            'notif_no_leidas':        notif_no_leidas,
            'alumnos_con_apoderado':  alumnos_con_apoderado,
        }
        return render(request, 'dashboard/profesor.html', context)

    # ── APODERADO ──────────────────────────────────────────────────────────
    elif user.rol == 'apoderado':
        try:
            apoderado = user.perfil_apoderado
        except Exception:
            return render(request, 'dashboard/apoderado.html', {
                'apoderado': None, 'datos_pupilos': [],
                'notifs_recibidas': [], 'notif_no_leidas': 0,
            })

        from asistencia.models import RegistroAsistencia

        datos_pupilos = []
        for alumno in apoderado.pupilos.select_related('usuario', 'curso').all():
            ausencias = RegistroAsistencia.objects.filter(
                alumno=alumno,
                estado__in=['ausente', 'atrasado', 'justificado']
            ).select_related('asignatura').order_by('-fecha')[:10]

            datos_pupilos.append({
                'alumno':                alumno,
                'promedio_general':      alumno.get_promedio_general(),
                'porcentaje_asistencia': alumno.get_porcentaje_asistencia(),
                'anotaciones_recientes': alumno.anotaciones.order_by('-fecha')[:3],
                'ausencias_recientes':   ausencias,
            })

        # Notificaciones del apoderado
        notifs_recibidas = Notificacion.objects.filter(
            destinatario=user
        ).select_related('remitente').order_by('-fecha_envio')[:5]

        notif_no_leidas = Notificacion.objects.filter(
            destinatario=user, leida=False
        ).count()

        context = {
            'apoderado':        apoderado,
            'datos_pupilos':    datos_pupilos,
            'notifs_recibidas': notifs_recibidas,
            'notif_no_leidas':  notif_no_leidas,
        }
        return render(request, 'dashboard/apoderado.html', context)

    # ── ALUMNO ─────────────────────────────────────────────────────────────
    elif user.rol == 'alumno':
        try:
            alumno = user.perfil_alumno
        except Exception:
            return render(request, 'dashboard/alumno.html', {'alumno': None})

        from notas.models import  PromedioAsignatura
        from asistencia.models import RegistroAsistencia
        from anotaciones.models import Anotacion
        from asignaturas.models import Asignatura

        # ── Promedios por asignatura ──────────────────────────────────────
        promedios = PromedioAsignatura.objects.filter(
            alumno=alumno
        ).select_related('asignatura', 'asignatura__profesor').order_by(
            'asignatura__nombre'
        )

        # Promedio general: media de los promedios por asignatura
        promedios_vals = [p.promedio for p in promedios if p.promedio is not None]
        if promedios_vals:

            promedio_general = round(sum(promedios_vals) / len(promedios_vals), 1)
        else:
            promedio_general = None

        # ── Asistencia ────────────────────────────────────────────────────
        asistencia_qs = RegistroAsistencia.objects.filter(alumno=alumno)
        total_dias = asistencia_qs.count()
        dias_presentes = asistencia_qs.filter(estado='presente').count()
        if total_dias > 0:
            porcentaje_asistencia = round((dias_presentes / total_dias) * 100, 1)
        else:
            porcentaje_asistencia = None

        # ── Anotaciones ───────────────────────────────────────────────────
        anotaciones = Anotacion.objects.filter(
            alumno=alumno
        ).select_related('creado_por').order_by('-fecha')[:5]

        # ── Notificaciones ────────────────────────────────────────────────
        notifs_recibidas = Notificacion.objects.filter(
            destinatario=user
        ).select_related('remitente').order_by('-fecha_envio')[:5]

        notif_no_leidas = Notificacion.objects.filter(
            destinatario=user, leida=False
        ).count()

        context = {
            'alumno':                alumno,
            'promedios':             promedios,
            'promedio_general':      promedio_general,
            'porcentaje_asistencia': porcentaje_asistencia,
            'anotaciones':           anotaciones,
            'notifs_recibidas':      notifs_recibidas,
            'notif_no_leidas':       notif_no_leidas,
        }
        return render(request, 'dashboard/alumno.html', context)

    return render(request, 'dashboard/sin_rol.html', {})
