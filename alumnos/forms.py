"""
APP: alumnos
ARCHIVO: forms.py

Formulario para gestión de alumnos.
Separado de views.py para mantener la separación de responsabilidades de Django.
"""
from django import forms
from .models import Alumno

# Clase CSS compartida para todos los campos del formulario
_INPUT = (
    "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 "
    "bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 "
    "focus:border-primary transition-all"
)


class AlumnoForm(forms.ModelForm):
    """Formulario para crear y editar alumnos."""

    class Meta:
        model  = Alumno
        fields = [
            'usuario', 'curso', 'apoderado',
            'fecha_nacimiento', 'numero_matricula', 'direccion', 'activo'
        ]
        widgets = {
            'usuario':          forms.Select(attrs={'class': _INPUT}),
            'curso':            forms.Select(attrs={'class': _INPUT}),
            'apoderado':        forms.Select(attrs={'class': _INPUT}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': _INPUT, 'type': 'date'}),
            'numero_matricula': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ej: 2026001'}),
            'direccion':        forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Dirección del alumno'}),
            'activo':           forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-primary cursor-pointer'}),
        }
        labels = {
            'usuario':          'Usuario del sistema',
            'curso':            'Curso',
            'apoderado':        'Apoderado',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'numero_matricula': 'Nº de matrícula',
            'direccion':        'Dirección',
            'activo':           'Alumno activo',
        }
