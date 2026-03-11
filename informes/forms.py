"""APP: informes - forms.py"""
from django import forms
from .models import Periodo, ComentarioInforme

INPUT    = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT   = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
DATE     = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
TEXTAREA = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"


class PeriodoForm(forms.ModelForm):
    class Meta:
        model  = Periodo
        fields = ['tipo', 'numero', 'anio', 'fecha_inicio', 'fecha_fin', 'activo']
        widgets = {
            'tipo':         forms.Select(attrs={'class': SELECT}),
            'numero':       forms.NumberInput(attrs={'class': INPUT, 'min': 1, 'max': 3}),
            'anio':         forms.NumberInput(attrs={'class': INPUT, 'min': 2020, 'max': 2099}),
            'fecha_inicio': forms.DateInput(attrs={'class': DATE, 'type': 'date'}),
            'fecha_fin':    forms.DateInput(attrs={'class': DATE, 'type': 'date'}),
            'activo':       forms.CheckboxInput(attrs={'class': 'w-4 h-4 accent-primary cursor-pointer'}),
        }
        labels = {
            'tipo':         'Tipo de período',
            'numero':       'Número (1, 2 o 3)',
            'anio':         'Año',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin':    'Fecha de término',
            'activo':       'Período activo',
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        fin    = cleaned.get('fecha_fin')
        tipo   = cleaned.get('tipo')
        numero = cleaned.get('numero')
        if tipo == Periodo.SEMESTRE and numero and numero > 2:
            raise forms.ValidationError('Los semestres solo pueden ser 1 o 2.')
        if inicio and fin and inicio >= fin:
            raise forms.ValidationError('La fecha de inicio debe ser anterior a la de término.')
        return cleaned


class ComentarioInformeForm(forms.ModelForm):
    class Meta:
        model  = ComentarioInforme
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': TEXTAREA,
                'rows': 5,
                'placeholder': 'Escribe aquí el comentario o apreciación general del alumno durante este período (opcional)...',
            }),
        }
        labels = {'comentario': 'Comentario del Profesor (opcional)'}
