from django import forms

CLASE_INPUT = 'w-full rounded-lg border border-slate-200 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 text-slate-900 focus:ring-2 focus:ring-primary focus:border-primary px-4 py-2.5 text-sm transition-all'

class ContactoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': CLASE_INPUT,
            'placeholder': 'Ej. Ana García',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': CLASE_INPUT,
            'placeholder': 'ana.garcia@colegio.edu',
        })
    )
    rol = forms.ChoiceField(
        choices=[
            ('', 'Selecciona tu rol'),
            ('Profesor/a', 'Profesor/a'),
            ('Padre/Madre de familia', 'Padre/Madre de familia'),
            ('Estudiante', 'Estudiante'),
            ('Administrativo', 'Administrativo'),
            ('Otro', 'Otro'),
        ],
        widget=forms.Select(attrs={
            'class': CLASE_INPUT,
        })
    )
    asunto = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': CLASE_INPUT,
            'placeholder': '¿En qué podemos ayudarte?',
        })
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': CLASE_INPUT + ' resize-none',
            'placeholder': 'Escribe aquí los detalles de tu consulta...',
            'rows': 5,
        })
    )