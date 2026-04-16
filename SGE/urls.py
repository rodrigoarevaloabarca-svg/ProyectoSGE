"""
URLs principales del proyecto SGE
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views
from SGE.views import error_400, error_403, error_404, error_500

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500

urlpatterns = [
    path("admin/", admin.site.urls),
    # Página principal - Landing del colegio
    path("", views.pagina_colegio, name="inicio"),
    path("plataforma/", lambda request: redirect("usuarios:login"), name="plataforma"),
    # URLs de cambio de contraseña de Django
    path("accounts/", include("django.contrib.auth.urls")),
    # Apps del sistema
    path("usuarios/", include("usuarios.urls", namespace="usuarios")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("alumnos/", include("alumnos.urls", namespace="alumnos")),
    path("profesores/", include("profesores.urls", namespace="profesores")),
    path("apoderados/", include("apoderados.urls", namespace="apoderados")),
    path("cursos/", include("cursos.urls", namespace="cursos")),
    path("asignaturas/", include("asignaturas.urls", namespace="asignaturas")),
    path("notas/", include("notas.urls", namespace="notas")),
    path("asistencia/", include("asistencia.urls", namespace="asistencia")),
    path("anotaciones/", include("anotaciones.urls", namespace="anotaciones")),
    path("informes/", include("informes.urls", namespace="informes")),
    path("historial/", include("historial.urls", namespace="historial")),
    # Páginas complementarias
    path("sobre_nosotros/", views.sobre_nosotros, name="sobre_nosotros"),
    path("ayuda/", views.ayuda, name="ayuda"),
    path("terminos/", views.terminos, name="terminos"),
    path("reglamento/", views.reglamento, name="reglamento"),
    path("directorio_docente/", views.directorio_docente, name="directorio_docente"),
    path("notificaciones/", include("notificaciones.urls", namespace="notificaciones")),
]

# ── Archivos estáticos y media ────────────────────────────────────────────────
# Se sirven SIEMPRE en desarrollo local (DEBUG=True o False)
# En producción real (servidor web) Nginx/Apache se encarga de esto
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# En producción (PythonAnywhere / Nginx), configurar en el panel web:
#   /static/ → BASE_DIR/staticfiles/
#   /media/  → BASE_DIR/media/
# NO usar django.views.static.serve en producción.
