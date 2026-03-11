from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def sobre_nosotros(request):
    return render(request, 'complementos_login/sobre_nosotros.html')
def contacto(request):
    return render(request, 'complementos_login/contacto.html')
def ayuda(request):
    return render(request, 'complementos_login/ayuda.html')
def terminos(request):
    return render(request, 'complementos_login/acce_politicas_terminos.html')
@login_required
def reglamento(request):
    return render(request, 'complementos_base/reglamento.html')
@login_required
def directorio_docente(request):
    return render(request, 'complementos_base/directorio_docente.html')


# ==========================================
# GESTIÓN DE ERRORES HTTP
# ==========================================
def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)