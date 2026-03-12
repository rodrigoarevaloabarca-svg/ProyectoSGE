"""APP: alumnos - views.py"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Alumno
from django import forms

INPUT  = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
DATE   = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"

def solo_admin(user):
    return user.is_authenticated and (user.es_admin)

def solo_staff(user):
    return user.is_authenticated and (user.es_admin or user.es_profesor)

class AlumnoForm(forms.ModelForm):
    class Meta:
        model  = Alumno
        fields = ['usuario', 'curso', 'apoderado', 'fecha_nacimiento', 'numero_matricula', 'direccion', 'activo']
        widgets = {
            'usuario':          forms.Select(attrs={'class': SELECT}),
            'curso':            forms.Select(attrs={'class': SELECT}),
            'apoderado':        forms.Select(attrs={'class': SELECT}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': DATE, 'type': 'date'}),
            'numero_matricula': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ej: 2026001'}),
            'direccion':        forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Dirección del alumno'}),
            'activo':           forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-primary cursor-pointer'}),
        }
        labels = {
            'usuario':          'Usuario del sistema',
            'curso':            'Curso',
            'apoderado':        'Apoderado',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'numero_matricula': 'N° de matrícula',
            'direccion':        'Dirección',
            'activo':           'Alumno activo',
        }


@login_required
@user_passes_test(solo_staff, login_url='dashboard:inicio')
def lista_alumnos(request):
    alumnos = Alumno.objects.filter(activo=True).select_related('usuario', 'curso__nivel')
    return render(request, 'alumnos/lista.html', {
        'alumnos': alumnos,
        'breadcrumbs': [
            {'label': 'Alumnos', 'url': ''},
        ],
    })


@login_required
#@user_passes_test(solo_staff, login_url='dashboard:inicio')Q no puedan entrar a menos q sea profesor o administrador
def detalle_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    return render(request, 'alumnos/detalle.html', {
        'alumno':                alumno,
        'promedios':             alumno.get_promedio_por_asignatura(),
        'promedio_general':      alumno.get_promedio_general(),
        'porcentaje_asistencia': alumno.get_porcentaje_asistencia(),
        'anotaciones':           alumno.anotaciones.order_by('-fecha')[:20],
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
        'form':  form,
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
        'form':  form,
        'titulo': 'Editar Alumno',
        'breadcrumbs': [
            {'label': 'Alumnos',              'url': reverse('alumnos:lista')},
            {'label': alumno.nombre_completo, 'url': reverse('alumnos:detalle', kwargs={'pk': pk})},
            {'label': 'Editar',               'url': ''},
        ],
    })
