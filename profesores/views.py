"""APP: profesores - views.py"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Profesor
from .forms import ProfesorForm


@login_required
def lista_profesores(request):
    profesores = Profesor.objects.filter(activo=True).select_related('usuario')
    return render(request, 'profesores/lista.html', {
        'profesores': profesores,
        'breadcrumbs': [
            {'label': 'Profesores', 'url': ''},
        ],
    })


@login_required
def detalle_profesor(request, pk):
    profesor    = get_object_or_404(Profesor, pk=pk)
    asignaturas = profesor.asignaturas.filter(activo=True).select_related('curso')
    return render(request, 'profesores/detalle.html', {
        'profesor':    profesor,
        'asignaturas': asignaturas,
        'breadcrumbs': [
            {'label': 'Profesores',             'url': reverse('profesores:lista')},
            {'label': profesor.nombre_completo, 'url': ''},
        ],
    })


@login_required
def crear_profesor(request):
    if request.method == 'POST':
        form = ProfesorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profesor creado exitosamente.')
            return redirect('profesores:lista')
    else:
        form = ProfesorForm()
    return render(request, 'profesores/form.html', {
        'form':  form,
        'titulo': 'Crear Profesor',
        'breadcrumbs': [
            {'label': 'Profesores', 'url': reverse('profesores:lista')},
            {'label': 'Crear',      'url': ''},
        ],
    })


@login_required
def editar_profesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        form = ProfesorForm(request.POST, request.FILES, instance=profesor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profesor actualizado exitosamente.')
            return redirect('profesores:detalle', pk=profesor.pk)
    else:
        form = ProfesorForm(instance=profesor)
    return render(request, 'profesores/form.html', {
        'form':  form,
        'titulo': 'Editar Profesor',
        'breadcrumbs': [
            {'label': 'Profesores',             'url': reverse('profesores:lista')},
            {'label': profesor.nombre_completo, 'url': reverse('profesores:detalle', kwargs={'pk': pk})},
            {'label': 'Editar',                 'url': ''},
        ],
    })


@login_required
def eliminar_profesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        profesor.activo = False
        profesor.save()
        messages.success(request, 'Profesor desactivado correctamente.')
        return redirect('profesores:lista')
    return render(request, 'confirm_delete.html', {
        'object':     profesor,
        'titulo':     f'Desactivar a {profesor.nombre_completo}',
        'cancel_url': 'profesores:lista',
        'breadcrumbs': [
            {'label': 'Profesores',             'url': reverse('profesores:lista')},
            {'label': profesor.nombre_completo, 'url': reverse('profesores:detalle', kwargs={'pk': pk})},
            {'label': 'Desactivar',             'url': ''},
        ],
    })
