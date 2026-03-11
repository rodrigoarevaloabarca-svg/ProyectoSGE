"""APP: cursos - views.py"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Curso, NivelEducacional
from django import forms

INPUT  = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"

class CursoForm(forms.ModelForm):
    class Meta:
        model  = Curso
        fields = ['nivel', 'grado', 'letra', 'anio_academico', 'profesor_jefe', 'activo']
        widgets = {
            'nivel':          forms.Select(attrs={'class': SELECT}),
            'grado':          forms.NumberInput(attrs={'class': INPUT, 'min': '1', 'max': '12'}),
            'letra':          forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ej: A, B, C'}),
            'anio_academico': forms.NumberInput(attrs={'class': INPUT, 'placeholder': '2026'}),
            'profesor_jefe':  forms.Select(attrs={'class': SELECT}),
            'activo':         forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-primary cursor-pointer'}),
        }
        labels = {
            'nivel':          'Nivel educacional',
            'grado':          'Grado',
            'letra':          'Letra del curso',
            'anio_academico': 'Año académico',
            'profesor_jefe':  'Profesor jefe',
            'activo':         'Curso activo',
        }


@login_required
def lista_cursos(request):
    cursos = Curso.objects.filter(activo=True).select_related(
        'nivel', 'profesor_jefe__usuario'
    ).order_by('nivel', 'grado', 'letra')
    return render(request, 'cursos/lista.html', {
        'cursos': cursos,
        'breadcrumbs': [
            {'label': 'Cursos', 'url': ''},
        ],
    })


@login_required
def detalle_curso(request, pk):
    curso       = get_object_or_404(Curso, pk=pk)
    alumnos     = curso.alumnos.filter(activo=True).select_related('usuario')
    asignaturas = curso.asignaturas.filter(activo=True).select_related('profesor__usuario')
    return render(request, 'cursos/detalle.html', {
        'curso':       curso,
        'alumnos':     alumnos,
        'asignaturas': asignaturas,
        'breadcrumbs': [
            {'label': 'Cursos',   'url': reverse('cursos:lista')},
            {'label': str(curso), 'url': ''},
        ],
    })


@login_required
def crear_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save()
            messages.success(request, f'Curso {curso} creado exitosamente.')
            return redirect('cursos:lista')
    else:
        form = CursoForm()
    return render(request, 'cursos/form.html', {
        'form':  form,
        'titulo': 'Crear Curso',
        'breadcrumbs': [
            {'label': 'Cursos', 'url': reverse('cursos:lista')},
            {'label': 'Crear',  'url': ''},
        ],
    })


@login_required
def editar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso actualizado.')
            return redirect('cursos:lista')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'cursos/form.html', {
        'form':  form,
        'titulo': 'Editar Curso',
        'curso':  curso,
        'breadcrumbs': [
            {'label': 'Cursos',   'url': reverse('cursos:lista')},
            {'label': str(curso), 'url': reverse('cursos:detalle', kwargs={'pk': pk})},
            {'label': 'Editar',   'url': ''},
        ],
    })
