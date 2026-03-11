"""APP: apoderados - forms.py"""
from django import forms
from .models import Apoderado

INPUT  = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"


class ApoderadoForm(forms.ModelForm):
    class Meta:
        model  = Apoderado
        fields = ['usuario', 'parentesco', 'ocupacion', 'activo']
        widgets = {
            'usuario':    forms.Select(attrs={'class': SELECT}),
            'parentesco': forms.TextInput(attrs={
                'class': INPUT,
                'placeholder': 'Ej: Padre, Madre, Tutor...',
            }),
            'ocupacion':  forms.TextInput(attrs={
                'class': INPUT,
                'placeholder': 'Ej: Ingeniero, Profesora...',
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 accent-primary cursor-pointer',
            }),
        }
        labels = {
            'usuario':    'Usuario del sistema',
            'parentesco': 'Parentesco con el alumno',
            'ocupacion':  'Ocupación',
            'activo':     'Apoderado activo',
        }
