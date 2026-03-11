"""APP: asistencia - views.py"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from .models import RegistroAsistencia
from alumnos.models import Alumno
from asignaturas.models import Asignatura


@login_required
def tomar_asistencia(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, pk=asignatura_id)
    alumnos    = Alumno.objects.filter(
        curso=asignatura.curso, activo=True
    ).select_related('usuario').order_by('usuario__last_name')

    fecha_hoy         = timezone.now().date()
    asistencia_exist  = RegistroAsistencia.objects.filter(
        asignatura=asignatura, fecha=fecha_hoy
    ).select_related('alumno')
    asistencia_dict   = {r.alumno.pk: r.estado for r in asistencia_exist}

    if request.method == 'POST':
        datos = [
            {'alumno_id': alumno.pk, 'estado': request.POST.get(f'estado_{alumno.pk}', 'presente')}
            for alumno in alumnos
        ]
        RegistroAsistencia.tomar_asistencia_curso(
            asignatura=asignatura,
            fecha=fecha_hoy,
            datos_asistencia=datos,
            profesor=request.user,
        )
        messages.success(request, f'Asistencia del {fecha_hoy} registrada exitosamente.')
        return redirect('asistencia:resumen_asignatura', asignatura_id=asignatura_id)

    alumnos_con_estado = [
        {'alumno': alumno, 'estado_actual': asistencia_dict.get(alumno.pk, 'presente')}
        for alumno in alumnos
    ]
    return render(request, 'asistencia/tomar_asistencia.html', {
        'asignatura':         asignatura,
        'alumnos_con_estado': alumnos_con_estado,
        'fecha_hoy':          fecha_hoy,
        'estados':            RegistroAsistencia.ESTADOS,
        'breadcrumbs': [
            {'label': 'Cursos',           'url': reverse('cursos:lista')},
            {'label': str(asignatura.curso), 'url': reverse('cursos:detalle', kwargs={'pk': asignatura.curso.pk})},
            {'label': asignatura.nombre,  'url': ''},
            {'label': 'Tomar asistencia', 'url': ''},
        ],
    })


@login_required
def resumen_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, pk=asignatura_id)
    registros  = RegistroAsistencia.objects.filter(
        asignatura=asignatura
    ).select_related('alumno__usuario').order_by('-fecha')
    return render(request, 'asistencia/resumen_asignatura.html', {
        'asignatura': asignatura,
        'registros':  registros,
        'breadcrumbs': [
            {'label': 'Cursos',              'url': reverse('cursos:lista')},
            {'label': str(asignatura.curso), 'url': reverse('cursos:detalle', kwargs={'pk': asignatura.curso.pk})},
            {'label': asignatura.nombre,     'url': ''},
            {'label': 'Asistencia',          'url': ''},
        ],
    })


@login_required
def asistencia_alumno(request, alumno_id):
    alumno    = get_object_or_404(Alumno, pk=alumno_id)
    registros = RegistroAsistencia.objects.filter(
        alumno=alumno
    ).select_related('asignatura').order_by('-fecha')

    total        = registros.count()
    presentes    = registros.filter(estado='presente').count()
    ausentes     = registros.filter(estado='ausente').count()
    atrasados    = registros.filter(estado='atrasado').count()
    justificados = registros.filter(estado='justificado').count()
    porcentaje   = round(presentes / total * 100, 1) if total > 0 else 0

    return render(request, 'asistencia/historial_alumno.html', {
        'alumno':   alumno,
        'registros': registros,
        'stats': {
            'total':        total,
            'presentes':    presentes,
            'ausentes':     ausentes,
            'atrasados':    atrasados,
            'justificados': justificados,
            'porcentaje':   porcentaje,
        },
        'breadcrumbs': [
            {'label': 'Alumnos',              'url': reverse('alumnos:lista')},
            {'label': alumno.nombre_completo, 'url': reverse('alumnos:detalle', kwargs={'pk': alumno_id})},
            {'label': 'Asistencia',           'url': ''},
        ],
    })
