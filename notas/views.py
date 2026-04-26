"""
APP: notas
ARCHIVO: views.py
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from alumnos.models import Alumno
from asignaturas.models import Asignatura
from cursos.models import Curso
from historial.utils import registrar_cambio_nota, snapshot_nota
from usuarios.decorators import puede_ver_alumno

from .forms import NotaForm
from .models import Nota, PromedioAsignatura


def solo_profesor_o_admin(user):
    return user.es_profesor or user.es_admin


@login_required
def libro_notas_curso(request, curso_id):
    # Solo admin y profesores pueden acceder al libro de notas de un curso.
    user = request.user
    if not (user.es_admin or user.es_profesor):
        messages.error(request, 'No tienes permiso para ver el libro de notas.')
        return redirect('dashboard:inicio')

    curso       = get_object_or_404(Curso, pk=curso_id)
    alumnos     = Alumno.objects.filter(curso=curso, activo=True).select_related('usuario')
    asignaturas = Asignatura.objects.filter(curso=curso, activo=True)

    # Optimizacion: una sola query en lugar de N*M individuales
    promedios_qs = PromedioAsignatura.objects.filter(
        alumno__in=alumnos, asignatura__in=asignaturas
    ).select_related('alumno', 'asignatura')
    promedios_map = {(p.alumno_id, p.asignatura_id): p.promedio for p in promedios_qs}

    libro = {}
    for alumno in alumnos:
        libro[alumno] = {}
        for asig in asignaturas:
            libro[alumno][asig] = promedios_map.get((alumno.pk, asig.pk))

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
@puede_ver_alumno('alumno_id')
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
            {'label': 'Libro de Notas',       'url': reverse('notas:libro', kwargs={'curso_id': alumno.curso.pk})},
            {'label': alumno.nombre_completo, 'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_profesor_o_admin, login_url='dashboard:inicio')
def agregar_nota(request, alumno_id, asignatura_id):
    alumno     = get_object_or_404(Alumno,     pk=alumno_id)
    asignatura = get_object_or_404(Asignatura, pk=asignatura_id)

    # Profesor solo puede agregar notas en sus propias asignaturas
    if request.user.es_profesor and asignatura.profesor != request.user.perfil_profesor:
        messages.error(request, 'Solo puedes agregar notas en tus propias asignaturas.')
        return redirect('dashboard:inicio')

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
            {'label': 'Libro de Notas',       'url': reverse('notas:libro', kwargs={'curso_id': alumno.curso.pk})},
            {'label': alumno.nombre_completo, 'url': reverse('notas:detalle', kwargs={'alumno_id': alumno_id, 'asignatura_id': asignatura_id})},
            {'label': 'Agregar Nota',         'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_profesor_o_admin, login_url='dashboard:inicio')
def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, pk=nota_id)

    # Profesor solo puede editar notas de sus propias asignaturas
    if request.user.es_profesor and nota.asignatura.profesor != request.user.perfil_profesor:
        messages.error(request, 'Solo puedes editar notas de tus propias asignaturas.')
        return redirect('dashboard:inicio')

    if request.method == 'POST':
        # Snapshot ANTES de guardar
        antes = snapshot_nota(nota)
        antes['_id']          = nota.pk
        antes['_descripcion'] = str(nota)

        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            # Snapshot DESPUÉS de guardar
            nota.refresh_from_db()
            despues = snapshot_nota(nota)
            registrar_cambio_nota(antes, despues, request.user)

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
            {'label': 'Libro de Notas',           'url': reverse('notas:libro', kwargs={'curso_id': nota.alumno.curso.pk})},
            {'label': nota.alumno.nombre_completo, 'url': reverse('notas:detalle', kwargs={'alumno_id': nota.alumno.pk, 'asignatura_id': nota.asignatura.pk})},
            {'label': 'Editar Nota',              'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_profesor_o_admin, login_url='dashboard:inicio')
def eliminar_nota(request, nota_id):
    nota          = get_object_or_404(Nota, pk=nota_id)
    alumno_id     = nota.alumno.pk
    asignatura_id = nota.asignatura.pk

    # Profesor solo puede eliminar notas de sus propias asignaturas
    if request.user.es_profesor and nota.asignatura.profesor != request.user.perfil_profesor:
        messages.error(request, 'Solo puedes eliminar notas de tus propias asignaturas.')
        return redirect('dashboard:inicio')

    if request.method == 'POST':
        # Snapshot ANTES de eliminar
        antes = snapshot_nota(nota)
        antes['_id']          = nota.pk
        antes['_descripcion'] = str(nota)
        registrar_cambio_nota(antes, None, request.user, accion='eliminacion')

        nota.delete()
        messages.warning(request, 'Nota eliminada.')
        return redirect('notas:detalle', alumno_id=alumno_id, asignatura_id=asignatura_id)

    return render(request, 'notas/confirmar_eliminar.html', {
        'nota': nota,
        'breadcrumbs': [
            {'label': 'Libro de Notas',           'url': reverse('notas:libro', kwargs={'curso_id': nota.alumno.curso.pk})},
            {'label': nota.alumno.nombre_completo, 'url': reverse('notas:detalle', kwargs={'alumno_id': nota.alumno.pk, 'asignatura_id': nota.asignatura.pk})},
            {'label': 'Eliminar Nota',            'url': ''},
        ],
    })
