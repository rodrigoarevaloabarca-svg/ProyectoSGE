"""
APP: alumnos
ARCHIVO: views.py

Vistas para gestión de alumnos.
Control de acceso por rol en cada vista:
  - lista_alumnos : admin y profesor (con paginación y filtro por curso)
  - detalle_alumno: admin, profesor, el propio alumno, apoderado de ese alumno
  - crear_alumno  : solo admin
  - editar_alumno : solo admin
"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Alumno
from .forms import AlumnoForm
from SGE.ia_utils import analizar_riesgo_alumno
from usuarios.decorators import puede_ver_alumno


# ── Predicados de rol ─────────────────────────────────────────────────────────

def solo_admin(user):
    return user.is_authenticated and user.es_admin


def solo_staff(user):
    return user.is_authenticated and (user.es_admin or user.es_profesor)


# ── Vistas ────────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(solo_staff, login_url='dashboard:inicio')
def lista_alumnos(request):
    # Filtro opcional por curso via GET (?curso=<id>)
    curso_id = request.GET.get('curso', '')

    alumnos_qs = Alumno.objects.filter(activo=True).select_related(
        'usuario', 'curso__nivel'
    ).order_by('usuario__last_name', 'usuario__first_name')

    if curso_id:
        alumnos_qs = alumnos_qs.filter(curso_id=curso_id)

    # Conteo antes de paginar (1 sola query, no usa alumnos.count en template)
    total = alumnos_qs.count()

    # Paginación: 20 alumnos por página
    paginator   = Paginator(alumnos_qs, 20)
    page_number = request.GET.get('page', 1)
    page_obj    = paginator.get_page(page_number)

    # Cursos para el filtro desplegable
    from cursos.models import Curso
    cursos = Curso.objects.filter(activo=True).select_related('nivel').order_by(
        'nivel', 'grado', 'letra'
    )

    return render(request, 'alumnos/lista.html', {
        'alumnos':  page_obj,
        'page_obj': page_obj,
        'total':    total,
        'cursos':   cursos,
        'curso_id': curso_id,
        'breadcrumbs': [
            {'label': 'Alumnos', 'url': ''},
        ],
    })


@login_required
@puede_ver_alumno('pk')
def detalle_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    user   = request.user

    analisis_ia = None
    if user.es_admin or user.es_profesor:
        import logging
        try:
            analisis_ia = analizar_riesgo_alumno(alumno)
        except Exception as e:
            logging.getLogger(__name__).error(
                "Error en analizar_riesgo_alumno para alumno %s: %s", alumno.pk, e
            )

    return render(request, 'alumnos/detalle.html', {
        'alumno':                alumno,
        'promedios':             alumno.get_promedio_por_asignatura(),
        'promedio_general':      alumno.get_promedio_general(),
        'porcentaje_asistencia': alumno.get_porcentaje_asistencia(),
        'anotaciones':           alumno.anotaciones.select_related('creado_por', 'asignatura').order_by('-fecha')[:20],
        'analisis_ia':           analisis_ia,
        'breadcrumbs': [
            {'label': 'Alumnos',              'url': reverse('alumnos:lista')},
            {'label': alumno.nombre_completo, 'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_admin, login_url='dashboard:inicio')
def crear_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumno creado exitosamente.')
            return redirect('alumnos:lista')
    else:
        form = AlumnoForm()

    return render(request, 'alumnos/form.html', {
        'form':   form,
        'titulo': 'Crear Alumno',
        'breadcrumbs': [
            {'label': 'Alumnos', 'url': reverse('alumnos:lista')},
            {'label': 'Crear',   'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_admin, login_url='dashboard:inicio')
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alumno actualizado.')
            return redirect('alumnos:detalle', pk=pk)
    else:
        form = AlumnoForm(instance=alumno)

    return render(request, 'alumnos/form.html', {
        'form':   form,
        'titulo': 'Editar Alumno',
        'breadcrumbs': [
            {'label': 'Alumnos',              'url': reverse('alumnos:lista')},
            {'label': alumno.nombre_completo, 'url': reverse('alumnos:detalle', kwargs={'pk': pk})},
            {'label': 'Editar',               'url': ''},
        ],
    })
