"""APP: usuarios - views.py"""
import base64
import io
import logging
import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView as _PasswordChangeView
from django.contrib.auth.views import PasswordResetConfirmView as _PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetView as _PasswordResetView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from .forms import LoginForm, UsuarioCreacionForm, UsuarioEdicionForm, UsuarioPerfilForm
from .models import Usuario

logger = logging.getLogger('sge.seguridad')

_RESET_COOLDOWN = 120  # segundos entre solicitudes de reset


class ResetConfirmContrasenaView(_PasswordResetConfirmView):
    """Confirmación de restablecimiento de contraseña con registro de auditoría."""
    template_name = 'registration/password_reset_confirm.html'
    success_url   = reverse_lazy('password_reset_complete')

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        if getattr(response, 'status_code', None) == 200 and hasattr(self, 'validlink') and not self.validlink:
            logger.warning(
                'RESET CONTRASEÑA | Enlace inválido o expirado | uid=%s | ip=%s',
                kwargs.get('uidb64', '—'),
                self.request.META.get('REMOTE_ADDR', '—'),
            )
        return response


    def form_valid(self, form):
        response = super().form_valid(form)
        from historial.models import HistorialCambio
        from historial.utils import registrar_evento_usuario
        ip = self.request.META.get('REMOTE_ADDR', '—')
        logger.warning(
            'RESET CONTRASEÑA COMPLETADO | usuario=%s | ip=%s',
            self.user.username if hasattr(self, 'user') and self.user else '—',
            ip,
        )
        if hasattr(self, 'user') and self.user:
            registrar_evento_usuario(
                usuario_pk=self.user.pk,
                accion=HistorialCambio.ACCION_CAMBIO_CONTRASENA,
                datos={'ip': ip, 'motivo': 'Restablecimiento de contraseña por correo'},
                modificado_por=self.user,
            )
        return response


def solo_admin(user):
    return user.is_authenticated and user.es_admin



# ── Autenticación ─────────────────────────────────────────────────────────────

class LoginPersonalizado(LoginView):
    template_name        = 'usuarios/login.html'
    authentication_form  = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:inicio')


class LogoutPersonalizado(LogoutView):
    next_page = reverse_lazy('usuarios:login')


# ── Contraseña ────────────────────────────────────────────────────────────────

class CambioContrasenaView(_PasswordChangeView):
    """Cambia la contraseña, mantiene la sesión activa y registra el evento."""
    template_name = 'registration/password_change_form.html'
    success_url   = reverse_lazy('usuarios:perfil')

    def form_valid(self, form):
        response = super().form_valid(form)  # ya llama update_session_auth_hash
        from historial.models import HistorialCambio
        from historial.utils import registrar_evento_usuario
        ip = self.request.META.get('REMOTE_ADDR', '—')
        logger.warning(
            'CAMBIO CONTRASEÑA | usuario=%s | ip=%s',
            self.request.user.username, ip,
        )
        registrar_evento_usuario(
            usuario_pk=self.request.user.pk,
            accion=HistorialCambio.ACCION_CAMBIO_CONTRASENA,
            datos={'ip': ip},
            modificado_por=self.request.user,
        )
        messages.success(self.request, 'Contraseña actualizada correctamente.')
        return response


class ResetContrasenaView(_PasswordResetView):
    """Solicitud de reset con throttle de sesión (120 s entre intentos)."""
    template_name = 'registration/password_reset_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            ultimo = request.session.get('_ultimo_reset')
            if ultimo and (time.time() - ultimo) < _RESET_COOLDOWN:
                restante = int(_RESET_COOLDOWN - (time.time() - ultimo))
                messages.warning(
                    request,
                    f'Debes esperar {restante} segundos antes de volver a solicitar un reset.',
                )
                return redirect('password_reset')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session['_ultimo_reset'] = time.time()
        logger.warning(
            'RESET CONTRASEÑA solicitado | email=%s | ip=%s',
            form.cleaned_data.get('email', ''),
            self.request.META.get('REMOTE_ADDR', '—'),
        )
        return super().form_valid(form)


# ── Perfil ────────────────────────────────────────────────────────────────────

@login_required
def perfil(request):
    tiene_2fa = False
    try:
        from django_otp.plugins.otp_totp.models import TOTPDevice
        tiene_2fa = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
    except Exception:
        pass

    if request.method == 'POST':
        form = UsuarioPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = UsuarioPerfilForm(instance=request.user)

    return render(request, 'usuarios/perfil.html', {
        'usuario':    request.user,
        'form':       form,
        'tiene_2fa':  tiene_2fa,
        'breadcrumbs': [{'label': 'Mi Perfil', 'url': ''}],
    })


# ── Gestión de usuarios (solo admin) ─────────────────────────────────────────

@login_required
@user_passes_test(solo_admin)
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('rol', 'last_name')
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,
        'breadcrumbs': [{'label': 'Usuarios', 'url': ''}],
    })


@login_required
@user_passes_test(solo_admin)
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreacionForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} creado exitosamente.')
            return redirect('usuarios:lista')
    else:
        form = UsuarioCreacionForm()
    return render(request, 'usuarios/form.html', {
        'form':   form,
        'titulo': 'Crear Usuario',
        'breadcrumbs': [
            {'label': 'Usuarios', 'url': reverse('usuarios:lista')},
            {'label': 'Crear',    'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_admin)
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    rol_anterior = usuario.rol
    if request.method == 'POST':
        form = UsuarioEdicionForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            guardado = form.save()
            if guardado.rol != rol_anterior:
                from historial.models import HistorialCambio
                from historial.utils import registrar_evento_usuario
                registrar_evento_usuario(
                    usuario_pk=guardado.pk,
                    accion=HistorialCambio.ACCION_CAMBIO_ROL,
                    datos={'rol_antes': rol_anterior, 'rol_despues': guardado.rol},
                    modificado_por=request.user,
                    descripcion=str(guardado),
                )
                logger.warning(
                    'CAMBIO ROL | usuario=%s | %s → %s | por=%s',
                    guardado.username, rol_anterior, guardado.rol, request.user.username,
                )
            messages.success(request, f'Usuario {guardado.get_full_name()} actualizado.')
            return redirect('usuarios:lista')
    else:
        form = UsuarioEdicionForm(instance=usuario)
    return render(request, 'usuarios/form.html', {
        'form':   form,
        'titulo': f'Editar {usuario.get_full_name() or usuario.username}',
        'breadcrumbs': [
            {'label': 'Usuarios',                                   'url': reverse('usuarios:lista')},
            {'label': usuario.get_full_name() or usuario.username,  'url': ''},
            {'label': 'Editar',                                     'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_admin)
def desactivar_usuario(request, pk):
    if request.method != 'POST':
        return redirect('usuarios:lista')
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('usuarios:lista')
    usuario.is_active = False
    usuario.save()
    from historial.models import HistorialCambio
    from historial.utils import registrar_evento_usuario
    registrar_evento_usuario(
        usuario_pk=usuario.pk,
        accion=HistorialCambio.ACCION_DESACTIVACION,
        datos={'is_active': False},
        modificado_por=request.user,
        descripcion=str(usuario),
    )
    logger.warning(
        'DESACTIVACIÓN | usuario=%s | por=%s',
        usuario.username, request.user.username,
    )
    messages.warning(request, f'Usuario {usuario.get_full_name()} desactivado.')
    return redirect('usuarios:lista')


# ── 2FA ───────────────────────────────────────────────────────────────────────

@login_required
def enrollar_2fa(request):
    try:
        from django_otp.plugins.otp_totp.models import TOTPDevice
    except ImportError:
        messages.error(request, '2FA no disponible en esta instalación.')
        return redirect('usuarios:perfil')

    dispositivos_confirmados = TOTPDevice.objects.filter(user=request.user, confirmed=True)

    if request.method == 'POST':
        if 'revocar' in request.POST:
            TOTPDevice.objects.filter(user=request.user).delete()
            messages.success(request, 'Autenticación de dos factores desactivada.')
            return redirect('usuarios:perfil')

        token = request.POST.get('token', '').strip()
        device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
        if device and device.verify_token(token):
            device.confirmed = True
            device.save()
            logger.warning(
                '2FA ACTIVADO | usuario=%s | ip=%s',
                request.user.username,
                request.META.get('REMOTE_ADDR', '—'),
            )
            messages.success(request, 'Autenticación de dos factores activada correctamente.')
            return redirect('usuarios:perfil')
        messages.error(request, 'Código incorrecto. Revisa tu aplicación e inténtalo de nuevo.')

    # Obtener o crear dispositivo pendiente de confirmación
    device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
    if not device:
        device = TOTPDevice.objects.create(
            user=request.user,
            name='Autenticador',
            confirmed=False,
        )

    # Generar QR base64
    import qrcode
    qr_img = qrcode.make(device.config_url)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render(request, 'usuarios/2fa_enrollar.html', {
        'dispositivos': dispositivos_confirmados,
        'qr_b64':       qr_b64,
        'breadcrumbs': [
            {'label': 'Mi Perfil', 'url': reverse('usuarios:perfil')},
            {'label': 'Configurar 2FA', 'url': ''},
        ],
    })
