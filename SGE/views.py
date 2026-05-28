from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def pagina_colegio(request):
    documentos = [
        {
            "icono": "gavel",
            "titulo": "Reglamento Interno",
            "resumen": "Normas de convivencia, derechos y deberes de los estudiantes, protocolos de actuación ante faltas, medidas disciplinarias, y disposiciones generales para la sana convivencia escolar.",
            "archivo": "doc/reglamento.pdf",
            "tamano": "2.4 MB",
        },
        {
            "icono": "assignment",
            "titulo": "Reglamento de Evaluación",
            "resumen": "Criterios de promoción, escalas de calificación (1.0 a 7.0), procedimientos de evaluación diferenciada, eximición, y requisitos de asistencia para la promoción escolar.",
            "archivo": "doc/reglamento_evaluaciones.pdf",
            "tamano": "1.8 MB",
        },
    ]
    return render(request, "colegio.html", {"documentos": documentos})


def sobre_nosotros(request):
    return render(request, "complementos_login/sobre_nosotros.html")


def ayuda(request):
    return render(request, "complementos_login/ayuda.html")


def terminos(request):
    return render(request, "complementos_login/acce_politicas_terminos.html")


@login_required
def reglamento(request):
    return render(request, "complementos_base/reglamento.html")


@login_required
def directorio_docente(request):
    return render(request, "complementos_base/directorio_docente.html")


# ==========================================
# GESTIÓN DE ERRORES HTTP
# ==========================================
def error_400(request, exception=None):
    return render(request, "errors/400.html", status=400)


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)
