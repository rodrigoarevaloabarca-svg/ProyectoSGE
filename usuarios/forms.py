"""
APP: usuarios
ARCHIVO: forms.py

Formularios para gestión de usuarios.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario


# ── Validador de RUT chileno ──────────────────────────────────────────────────

def _validar_dv_rut(rut_limpio):
    """
    Valida el dígito verificador de un RUT chileno.
    Recibe el RUT sin puntos y con guión (ej: '12345678-9' o '12345678-k').
    Retorna True si el dígito verificador es correcto.
    """
    try:
        cuerpo, dv = rut_limpio.lower().split('-')
        cuerpo = int(cuerpo)
    except (ValueError, AttributeError):
        return False

    suma, multiplo = 0, 2
    while cuerpo:
        suma     += (cuerpo % 10) * multiplo
        cuerpo   //= 10
        multiplo  = 2 if multiplo == 7 else multiplo + 1

    resultado  = 11 - (suma % 11)
    dv_esperado = 'k' if resultado == 10 else ('0' if resultado == 11 else str(resultado))
    return dv == dv_esperado


def _limpiar_rut(rut):
    """Normaliza el RUT: elimina puntos, espacios y convierte a minúsculas."""
    return rut.replace('.', '').replace(' ', '').strip().lower()


# ── Formularios ───────────────────────────────────────────────────────────────

class LoginForm(AuthenticationForm):
    """
    Formulario de login personalizado.
    Hereda toda la validación de Django, solo ajustamos widgets CSS.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class':      'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus':   True,
        }),
        label='Usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Contraseña',
        }),
        label='Contraseña'
    )


class UsuarioCreacionForm(UserCreationForm):
    """
    Formulario para crear nuevos usuarios.
    Extiende UserCreationForm que ya valida contraseñas.
    Incluye validación completa del dígito verificador del RUT chileno.
    """
    class Meta:
        model  = Usuario
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'rut', 'telefono', 'rol',
            'foto_perfil', 'is_active',
        ]
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'rut':        forms.TextInput(attrs={
                              'class': 'form-control',
                              'placeholder': '12345678-9',
                          }),
            'telefono':   forms.TextInput(attrs={'class': 'form-control'}),
            'rol':        forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_rut(self):
        """
        Valida formato Y dígito verificador del RUT chileno.
        Acepta: '12.345.678-9', '12345678-9', '12345678-K'
        """
        rut = self.cleaned_data.get('rut')
        if not rut:
            return rut

        rut_limpio = _limpiar_rut(rut)

        if '-' not in rut_limpio:
            raise forms.ValidationError('El RUT debe tener el formato 12345678-9.')

        if not _validar_dv_rut(rut_limpio):
            raise forms.ValidationError(
                'El dígito verificador del RUT es incorrecto. '
                'Verifica que el RUT sea correcto.'
            )

        return rut_limpio

    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto:
            if foto.size > 2 * 1024 * 1024:
                raise forms.ValidationError('La imagen no puede superar 2 MB.')
            ext = foto.name.rsplit('.', 1)[-1].lower() if '.' in foto.name else ''
            if ext not in ('jpg', 'jpeg', 'png', 'webp'):
                raise forms.ValidationError('Solo se permiten imágenes JPG, PNG o WebP.')
            try:
                from PIL import Image
                img = Image.open(foto)
                img.verify()
                foto.seek(0)
            except Exception:
                raise forms.ValidationError('El archivo no es una imagen válida.')
        return foto


class UsuarioEdicionForm(forms.ModelForm):
    """
    Formulario para editar un usuario existente (sin cambiar contraseña).
    Incluye la misma validación de RUT que UsuarioCreacionForm.
    """
    class Meta:
        model  = Usuario
        fields = [
            'first_name', 'last_name', 'email',
            'rut', 'telefono', 'rol', 'foto_perfil', 'is_active',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'rut':        forms.TextInput(attrs={
                              'class': 'form-control',
                              'placeholder': '12345678-9',
                          }),
            'telefono':   forms.TextInput(attrs={'class': 'form-control'}),
            'rol':        forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            return rut

        rut_limpio = _limpiar_rut(rut)

        if '-' not in rut_limpio:
            raise forms.ValidationError('El RUT debe tener el formato 12345678-9.')

        if not _validar_dv_rut(rut_limpio):
            raise forms.ValidationError(
                'El dígito verificador del RUT es incorrecto. '
                'Verifica que el RUT sea correcto.'
            )

        return rut_limpio

    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        if foto and hasattr(foto, 'size'):
            if foto.size > 2 * 1024 * 1024:
                raise forms.ValidationError('La imagen no puede superar 2 MB.')
            ext = foto.name.rsplit('.', 1)[-1].lower() if '.' in foto.name else ''
            if ext not in ('jpg', 'jpeg', 'png', 'webp'):
                raise forms.ValidationError('Solo se permiten imágenes JPG, PNG o WebP.')
            try:
                from PIL import Image
                img = Image.open(foto)
                img.verify()
                foto.seek(0)
            except Exception:
                raise forms.ValidationError('El archivo no es una imagen válida.')
        return foto

class UsuarioPerfilForm(UsuarioEdicionForm):
    """
    Formulario para que el propio usuario edite su perfil.
    Excluimos campos sensibles como 'rol' e 'is_active'.
    """
    class Meta(UsuarioEdicionForm.Meta):
        fields = [
            'first_name', 'last_name', 'email',
            'rut', 'telefono', 'foto_perfil',
        ]
