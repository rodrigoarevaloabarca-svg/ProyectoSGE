"""APP: asignaturas - views.py"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Asignatura
from cursos.models import Curso
from django import forms

INPUT  = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model  = Asignatura
        fields = ['nombre', 'curso', 'profesor', 'horas_semanales', 'activo']
        widgets = {
            'nombre':          forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ej: Matemáticas'}),
            'curso':           forms.Select(attrs={'class': SELECT}),
            'profesor':        forms.Select(attrs={'class': SELECT}),
            'horas_semanales': forms.NumberInput(attrs={'class': INPUT, 'min': '1', 'max': '10'}),
            'activo':          forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-primary cursor-pointer'}),
        }
        labels = {
            'nombre':          'Nombre de la asignatura',
            'curso':           'Curso',
            'profesor':        'Profesor a cargo',
            'horas_semanales': 'Horas semanales',
            'activo':          'Asignatura activa',
        }


@login_required
def lista_asignaturas(request):
    asignaturas = Asignatura.objects.filter(activo=True).select_related('curso', 'profesor__usuario')
    return render(request, 'asignaturas/lista.html', {
        'asignaturas': asignaturas,
        'breadcrumbs': [
            {'label': 'Asignaturas', 'url': ''},
        ],
    })


@login_required
def asignaturas_por_curso(request, curso_id):
    curso       = get_object_or_404(Curso, pk=curso_id)
    asignaturas = Asignatura.objects.filter(curso=curso, activo=True).select_related('profesor__usuario')
    return render(request, 'asignaturas/por_curso.html', {
        'curso':       curso,
        'asignaturas': asignaturas,
        'breadcrumbs': [
            {'label': 'Cursos',      'url': reverse('cursos:lista')},
            {'label': str(curso),    'url': reverse('cursos:detalle', kwargs={'pk': curso_id})},
            {'label': 'Asignaturas', 'url': ''},
        ],
    })


@login_required
def crear_asignatura(request):
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignatura creada exitosamente.')
            return redirect('asignaturas:lista')
    else:
        form = AsignaturaForm()
    return render(request, 'asignaturas/form.html', {
        'form':  form,
        'titulo': 'Crear Asignatura',
        'breadcrumbs': [
            {'label': 'Asignaturas', 'url': reverse('asignaturas:lista')},
            {'label': 'Crear',       'url': ''},
        ],
    })


@login_required
def editar_asignatura(request, pk):
    asignatura = get_object_or_404(Asignatura, pk=pk)
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignatura actualizada.')
            return redirect('asignaturas:lista')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'asignaturas/form.html', {
        'form':  form,
        'titulo': 'Editar Asignatura',
        'breadcrumbs': [
            {'label': 'Asignaturas',    'url': reverse('asignaturas:lista')},
            {'label': asignatura.nombre,'url': ''},
            {'label': 'Editar',         'url': ''},
        ],
    })
