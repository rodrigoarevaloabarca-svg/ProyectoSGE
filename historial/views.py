"""
APP: historial
ARCHIVO: views.py

Vista de auditoría: solo accesible para administradores.
Permite filtrar por módulo, usuario y rango de fechas.
"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import HistorialCambio
from usuarios.models import Usuario


def solo_admin(user):
    return user.is_authenticated and user.es_admin


@login_required
@user_passes_test(solo_admin, login_url='dashboard:inicio')
def lista_historial(request):
    qs = HistorialCambio.objects.select_related('modificado_por').all()

    # ── Filtros ──────────────────────────────────────────────────────────
    modelo   = request.GET.get('modelo', '')
    usuario  = request.GET.get('usuario', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if modelo:
        qs = qs.filter(modelo=modelo)
    if usuario:
        qs = qs.filter(modificado_por__id=usuario)
    if fecha_desde:
        qs = qs.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha__date__lte=fecha_hasta)

    # Solo mostrar usuarios staff en el filtro
    usuarios_staff = Usuario.objects.filter(
        rol__in=['admin', 'profesor']
    ).order_by('last_name')

    return render(request, 'historial/lista.html', {
        'historial':      qs[:100],  # máximo 100 registros por página
        'usuarios_staff': usuarios_staff,
        'filtros': {
            'modelo':      modelo,
            'usuario':     usuario,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        },
        'breadcrumbs': [
            {'label': 'Historial de Cambios', 'url': ''},
        ],
    })
