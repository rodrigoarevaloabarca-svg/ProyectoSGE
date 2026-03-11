"""
APP: notas
ARCHIVO: views.py
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from .models import Nota, PromedioAsignatura
from .forms import NotaForm
from alumnos.models import Alumno
from asignaturas.models import Asignatura
from cursos.models import Curso


def solo_profesor_o_admin(user):
    return user.es_profesor or user.es_admin


@login_required
def libro_notas_curso(request, curso_id):
    curso       = get_object_or_404(Curso, pk=curso_id)
    alumnos     = Alumno.objects.filter(curso=curso, activo=True).select_related('usuario')
    asignaturas = Asignatura.objects.filter(curso=curso, activo=True)

    libro = {}
    for alumno in alumnos:
        libro[alumno] = {}
        for asig in asignaturas:
            try:
                promedio_obj = PromedioAsignatura.objects.get(alumno=alumno, asignatura=asig)
                libro[alumno][asig] = promedio_obj.promedio
            except PromedioAsignatura.DoesNotExist:
                libro[alumno][asig] = None

    return render(request, 'notas/libro_notas.html', {
        'curso':       curso,
        'alumnos':     alumnos,
        'asignaturas': asignaturas,
        'libro':       libro,
        'breadcrumbs': [
            {'label': 'Libro de Notas', 'url': ''},
        ],
    })


@login_required
def notas_alumno_asignatura(request, alumno_id, asignatura_id):
    alumno     = get_object_or_404(Alumno,     pk=alumno_id)
    asignatura = get_object_or_404(Asignatura, pk=asignatura_id)
    notas = Nota.objects.filter(
        alumno=alumno, asignatura=asignatura
    ).order_by('fecha')

    promedio = None
    if notas.exists():
        valores  = [float(n.valor) for n in notas]
        promedio = round(sum(valores) / len(valores), 1)

    return render(request, 'notas/notas_detalle.html', {
        'alumno':      alumno,
        'asignatura':  asignatura,
        'notas':       notas,
        'promedio':    promedio,
        'breadcrumbs': [
            {'label': 'Libro de Notas',        'url': reverse('notas:libro', kwargs={'curso_id': alumno.curso.pk})},
            {'label': alumno.nombre_completo,  'url': ''},
        ],
    })


@login_required
def agregar_nota(request, alumno_id, asignatura_id):
    alumno     = get_object_or_404(Alumno,     pk=alumno_id)
    asignatura = get_object_or_404(Asignatura, pk=asignatura_id)

    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.alumno        = alumno
            nota.asignatura    = asignatura
            nota.ingresado_por = request.user
            nota.save()
            messages.success(request, f'Nota {nota.valor} agregada exitosamente.')
            return redirect('notas:detalle', alumno_id=alumno_id, asignatura_id=asignatura_id)
    else:
        form = NotaForm()

    return render(request, 'notas/agregar_nota.html', {
        'form':        form,
        'alumno':      alumno,
        'asignatura':  asignatura,
        'breadcrumbs': [
            {'label': 'Libro de Notas',   'url': reverse('notas:libro', kwargs={'curso_id': alumno.curso.pk})},
            {'label': alumno.nombre_completo, 'url': reverse('notas:detalle', kwargs={'alumno_id': alumno_id, 'asignatura_id': asignatura_id})},
            {'label': 'Agregar Nota',     'url': ''},
        ],
    })


@login_required
def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, pk=nota_id)

    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nota actualizada.')
            return redirect('notas:detalle',
                            alumno_id=nota.alumno.pk,
                            asignatura_id=nota.asignatura.pk)
    else:
        form = NotaForm(instance=nota)

    return render(request, 'notas/editar_nota.html', {
        'form':  form,
        'nota':  nota,
        'breadcrumbs': [
            {'label': 'Libro de Notas',        'url': reverse('notas:libro', kwargs={'curso_id': nota.alumno.curso.pk})},
            {'label': nota.alumno.nombre_completo, 'url': reverse('notas:detalle', kwargs={'alumno_id': nota.alumno.pk, 'asignatura_id': nota.asignatura.pk})},
            {'label': 'Editar Nota',           'url': ''},
        ],
    })


@login_required
def eliminar_nota(request, nota_id):
    nota          = get_object_or_404(Nota, pk=nota_id)
    alumno_id     = nota.alumno.pk
    asignatura_id = nota.asignatura.pk

    if request.method == 'POST':
        nota.delete()
        messages.warning(request, 'Nota eliminada.')
        return redirect('notas:detalle', alumno_id=alumno_id, asignatura_id=asignatura_id)

    return render(request, 'notas/confirmar_eliminar.html', {
        'nota': nota,
        'breadcrumbs': [
            {'label': 'Libro de Notas',        'url': reverse('notas:libro', kwargs={'curso_id': nota.alumno.curso.pk})},
            {'label': nota.alumno.nombre_completo, 'url': reverse('notas:detalle', kwargs={'alumno_id': nota.alumno.pk, 'asignatura_id': nota.asignatura.pk})},
            {'label': 'Eliminar Nota',         'url': ''},
        ],
    })
