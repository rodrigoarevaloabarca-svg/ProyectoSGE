"""
APP: usuarios
ARCHIVO: forms.py

Formularios para gestión de usuarios.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    """
    Formulario de login personalizado.
    Hereda toda la validación de Django, solo cambiamos clases CSS.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        }),
        label='Usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña'
    )


class UsuarioCreacionForm(UserCreationForm):
    """
    Formulario para crear nuevos usuarios.
    Extiende UserCreationForm que ya valida contraseñas.
    """
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'rut', 'telefono', 'rol',
            'foto_perfil', 'is_active'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_rut(self):
        """Validación básica del formato RUT chileno."""
        rut = self.cleaned_data.get('rut')
        if rut:
            rut = rut.replace('.', '').strip()
            if '-' not in rut:
                raise forms.ValidationError('El RUT debe tener el formato 12345678-9')
        return rut


class UsuarioEdicionForm(forms.ModelForm):
    """Formulario para editar un usuario existente (sin cambiar contraseña)."""
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email',
            'rut', 'telefono', 'rol', 'foto_perfil', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }
