"""
URLs principales del proyecto SGE
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path

from SGE.views import error_400, error_403, error_404, error_500
from usuarios.views import CambioContrasenaView, ResetContrasenaView

from . import views

# Proteger el panel admin con OTP cuando django-otp está instalado
try:
    from django_otp.admin import OTPAdminSite

    class _SGEAdminSite(OTPAdminSite):
        """Requiere 2FA solo si el usuario ya tiene un dispositivo enrollado."""
        def has_permission(self, request):
            if not super(OTPAdminSite.__bases__[0], self).has_permission(request):
                return False
            try:
                from django_otp.plugins.otp_totp.models import TOTPDevice
                if not TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
                    return True  # sin dispositivo: acceso permitido para poder enrollar
            except Exception:
                return True
            return request.user.is_verified()

    admin.site.__class__ = _SGEAdminSite
except ImportError:
    pass

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500

urlpatterns = [
    path("admin/", admin.site.urls),
    # Página principal
    path("", views.pagina_colegio, name="inicio"),
    path("plataforma/", lambda request: redirect("usuarios:login"), name="plataforma"),
    # Cambio / reset de contraseña (vistas personalizadas con logging y throttle)
    path("accounts/password_change/",
         CambioContrasenaView.as_view(), name="password_change"),
    path("accounts/password_change/done/",
         auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("accounts/password_reset/",
         ResetContrasenaView.as_view(), name="password_reset"),
    path("accounts/password_reset/done/",
         auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("accounts/reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("accounts/reset/done/",
         auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # Apps del sistema
    path("usuarios/",     include("usuarios.urls",      namespace="usuarios")),
    path("dashboard/",    include("dashboard.urls",     namespace="dashboard")),
    path("alumnos/",      include("alumnos.urls",       namespace="alumnos")),
    path("profesores/",   include("profesores.urls",    namespace="profesores")),
    path("apoderados/",   include("apoderados.urls",    namespace="apoderados")),
    path("cursos/",       include("cursos.urls",        namespace="cursos")),
    path("asignaturas/",  include("asignaturas.urls",   namespace="asignaturas")),
    path("notas/",        include("notas.urls",         namespace="notas")),
    path("asistencia/",   include("asistencia.urls",    namespace="asistencia")),
    path("anotaciones/",  include("anotaciones.urls",   namespace="anotaciones")),
    path("informes/",     include("informes.urls",      namespace="informes")),
    path("historial/",    include("historial.urls",     namespace="historial")),
    # Páginas complementarias
    path("sobre_nosotros/",     views.sobre_nosotros,     name="sobre_nosotros"),
    path("ayuda/",              views.ayuda,               name="ayuda"),
    path("terminos/",           views.terminos,            name="terminos"),
    path("reglamento/",         views.reglamento,          name="reglamento"),
    path("directorio_docente/", views.directorio_docente,  name="directorio_docente"),
    path("notificaciones/",     include("notificaciones.urls", namespace="notificaciones")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
