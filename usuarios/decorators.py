"""
APP: usuarios
ARCHIVO: decorators.py

Decoradores de control de acceso reutilizables.
"""
from functools import wraps
from django.shortcuts import redirect


def solo_admin(view_func):
    """Permite acceso solo a usuarios con rol admin."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.es_admin:
            return redirect('dashboard:inicio')
        return view_func(request, *args, **kwargs)
    return wrapper


def solo_admin_o_profesor(view_func):
    """Permite acceso a admin y profesores."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:inicio')
        if not (request.user.es_admin or request.user.es_profesor):
            return redirect('dashboard:inicio')
        return view_func(request, *args, **kwargs)
    return wrapper
