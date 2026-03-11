"""APP: profesores - forms.py"""
from django import forms
from .models import Profesor

INPUT  = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
DATE   = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"


class ProfesorForm(forms.ModelForm):
    class Meta:
        model  = Profesor    # ← modelo real, NO comentado
        fields = ['usuario', 'especialidad', 'fecha_ingreso', 'activo']
        widgets = {
            'usuario': forms.Select(attrs={'class': SELECT}),
            'especialidad': forms.TextInput(attrs={
                'class': INPUT,
                'placeholder': 'Ej: Matemáticas, Lenguaje...',
            }),
            'fecha_ingreso': forms.DateInput(attrs={
                'class': DATE,
                'type': 'date',
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 accent-primary cursor-pointer',
            }),
        }
        labels = {
            'usuario':        'Usuario del sistema',
            'especialidad':   'Especialidad / Mención',
            'fecha_ingreso':  'Fecha de ingreso',
            'activo':         'Profesor activo',
        }
