"""APP: anotaciones - views.py"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Anotacion
from alumnos.models import Alumno
from django import forms

INPUT    = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT   = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
TEXTAREA = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"
DATE     = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"



class AnotacionForm(forms.ModelForm):
    class Meta:
        model  = Anotacion
        fields = ['tipo', 'categoria', 'descripcion', 'fecha', 'asignatura']
        widgets = {
            'tipo':        forms.Select(attrs={'class': SELECT}),
            'categoria':   forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Ej: Conducta, Académico...'}),
            'descripcion': forms.Textarea(attrs={'class': TEXTAREA, 'rows': 4, 'placeholder': 'Describe la anotación...'}),
            'fecha':       forms.DateInput(attrs={'class': DATE, 'type': 'date'}),
            'asignatura':  forms.Select(attrs={'class': SELECT}),
        }
        labels = {
            'tipo':        'Tipo de anotación',
            'categoria':   'Categoría',
            'descripcion': 'Descripción',
            'fecha':       'Fecha',
            'asignatura':  'Asignatura relacionada',
        }

def solo_staff(user):
    return user.is_authenticated and (user.es_admin or user.es_profesor)
@login_required
def anotaciones_alumno(request, alumno_id):
    alumno      = get_object_or_404(Alumno, pk=alumno_id)
    anotaciones = alumno.anotaciones.order_by('-fecha').select_related('creado_por', 'asignatura')
    return render(request, 'anotaciones/lista.html', {
        'alumno':      alumno,
        'anotaciones': anotaciones,
        'breadcrumbs': [
            {'label': 'Alumnos',              'url': reverse('alumnos:lista')},
            {'label': alumno.nombre_completo, 'url': reverse('alumnos:detalle', kwargs={'pk': alumno_id})},
            {'label': 'Anotaciones',          'url': ''},
        ],
    })

@login_required
@user_passes_test(solo_staff, login_url='dashboard:inicio')
def crear_anotacion(request, alumno_id):
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    if request.method == 'POST':
        form = AnotacionForm(request.POST)
        if form.is_valid():
            anotacion            = form.save(commit=False)
            anotacion.alumno     = alumno
            anotacion.creado_por = request.user
            anotacion.save()
            messages.success(request, 'Anotación registrada.')
            return redirect('anotaciones:alumno', alumno_id=alumno_id)
    else:
        form = AnotacionForm()
    return render(request, 'anotaciones/form.html', {
        'form':   form,
        'alumno': alumno,
        'breadcrumbs': [
            {'label': 'Alumnos',              'url': reverse('alumnos:lista')},
            {'label': alumno.nombre_completo, 'url': reverse('alumnos:detalle', kwargs={'pk': alumno_id})},
            {'label': 'Anotaciones',          'url': reverse('anotaciones:alumno', kwargs={'alumno_id': alumno_id})},
            {'label': 'Nueva anotación',      'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_staff, login_url='dashboard:inicio')
def editar_anotacion(request, pk):
    anotacion = get_object_or_404(Anotacion, pk=pk)
    alumno    = anotacion.alumno
    if request.method == 'POST':
        form = AnotacionForm(request.POST, instance=anotacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anotación actualizada.')
            return redirect('anotaciones:alumno', alumno_id=alumno.pk)
    else:
        form = AnotacionForm(instance=anotacion)
    return render(request, 'anotaciones/form.html', {
        'form':   form,
        'alumno': alumno,
        'breadcrumbs': [
            {'label': 'Alumnos',              'url': reverse('alumnos:lista')},
            {'label': alumno.nombre_completo, 'url': reverse('alumnos:detalle', kwargs={'pk': alumno.pk})},
            {'label': 'Anotaciones',          'url': reverse('anotaciones:alumno', kwargs={'alumno_id': alumno.pk})},
            {'label': 'Editar anotación',     'url': ''},
        ],
    })
