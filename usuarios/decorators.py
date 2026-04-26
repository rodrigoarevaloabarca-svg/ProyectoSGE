"""
APP: usuarios
ARCHIVO: decorators.py

Decoradores de control de acceso reutilizables.
"""
from functools import wraps

from django.contrib import messages
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


def puede_ver_alumno(alumno_kwarg='pk'):
    """
    Permite ver datos de un alumno específico según el rol:
      - Admin / Profesor : cualquier alumno
      - Apoderado        : solo sus pupilos
      - Alumno           : solo su propio perfil
    Uso: @puede_ver_alumno('pk') o @puede_ver_alumno('alumno_id')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('dashboard:inicio')
            user = request.user
            alumno_pk = kwargs.get(alumno_kwarg)
            if user.es_admin or user.es_profesor:
                return view_func(request, *args, **kwargs)
            if user.es_apoderado:
                perfil = getattr(user, 'perfil_apoderado', None)
                if perfil and perfil.pupilos.filter(pk=alumno_pk).exists():
                    return view_func(request, *args, **kwargs)
            elif user.es_alumno:
                perfil = getattr(user, 'perfil_alumno', None)
                if perfil and perfil.pk == alumno_pk:
                    return view_func(request, *args, **kwargs)
            messages.error(request, 'No tienes permiso para acceder a este alumno.')
            return redirect('dashboard:inicio')
        return wrapper
    return decorator
