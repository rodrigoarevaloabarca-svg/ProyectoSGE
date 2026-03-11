"""APP: apoderados - views.py"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Apoderado
from .forms import ApoderadoForm


@login_required
def lista_apoderados(request):
    apoderados = Apoderado.objects.filter(activo=True).select_related('usuario')
    return render(request, 'apoderados/lista.html', {
        'apoderados': apoderados,
        'breadcrumbs': [
            {'label': 'Apoderados', 'url': ''},
        ],
    })


@login_required
def detalle_apoderado(request, pk):
    apoderado = get_object_or_404(Apoderado, pk=pk)
    return render(request, 'apoderados/detalle.html', {
        'apoderado': apoderado,
        'breadcrumbs': [
            {'label': 'Apoderados',                'url': reverse('apoderados:lista')},
            {'label': apoderado.nombre_completo,   'url': ''},
        ],
    })


@login_required
def crear_apoderado(request):
    if request.method == 'POST':
        form = ApoderadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Apoderado creado exitosamente.')
            return redirect('apoderados:lista')
    else:
        form = ApoderadoForm()
    return render(request, 'apoderados/form.html', {
        'form':  form,
        'titulo': 'Crear Apoderado',
        'breadcrumbs': [
            {'label': 'Apoderados', 'url': reverse('apoderados:lista')},
            {'label': 'Crear',      'url': ''},
        ],
    })


@login_required
def editar_apoderado(request, pk):
    apoderado = get_object_or_404(Apoderado, pk=pk)
    if request.method == 'POST':
        form = ApoderadoForm(request.POST, instance=apoderado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Apoderado actualizado exitosamente.')
            return redirect('apoderados:detalle', pk=apoderado.pk)
    else:
        form = ApoderadoForm(instance=apoderado)
    return render(request, 'apoderados/form.html', {
        'form':  form,
        'titulo': 'Editar Apoderado',
        'breadcrumbs': [
            {'label': 'Apoderados',              'url': reverse('apoderados:lista')},
            {'label': apoderado.nombre_completo, 'url': reverse('apoderados:detalle', kwargs={'pk': pk})},
            {'label': 'Editar',                  'url': ''},
        ],
    })


@login_required
def eliminar_apoderado(request, pk):
    apoderado = get_object_or_404(Apoderado, pk=pk)
    if request.method == 'POST':
        apoderado.activo = False
        apoderado.save()
        messages.success(request, 'Apoderado desactivado.')
        return redirect('apoderados:lista')
    return render(request, 'confirm_delete.html', {
        'object':     apoderado,
        'titulo':     f'Desactivar a {apoderado.nombre_completo}',
        'cancel_url': 'apoderados:lista',
        'breadcrumbs': [
            {'label': 'Apoderados',              'url': reverse('apoderados:lista')},
            {'label': apoderado.nombre_completo, 'url': reverse('apoderados:detalle', kwargs={'pk': pk})},
            {'label': 'Desactivar',              'url': ''},
        ],
    })
