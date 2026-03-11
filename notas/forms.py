"""APP: notas - forms.py"""
from django import forms
from .models import Nota

FIELD_CSS = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
SELECT_CSS = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
TEXTAREA_CSS = "w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none"

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['tipo_evaluacion', 'valor', 'fecha', 'descripcion']
        widgets = {
            'tipo_evaluacion': forms.Select(attrs={'class': SELECT_CSS}),
            'valor': forms.NumberInput(attrs={
                'class': FIELD_CSS,
                'step': '0.1',
                'min': '1.0',
                'max': '7.0',
                'placeholder': 'Ej: 5.5'
            }),
            'fecha': forms.DateInput(attrs={
                'class': FIELD_CSS,
                'type': 'date'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': FIELD_CSS,
                'placeholder': 'Ej: Prueba Unidad 2'
            }),
        }

    def clean_valor(self):
        """Validación adicional del valor de la nota."""
        valor = self.cleaned_data.get('valor')
        if valor is not None:
            if valor < 1.0 or valor > 7.0:
                raise forms.ValidationError('La nota debe estar entre 1.0 y 7.0')
        return valor
