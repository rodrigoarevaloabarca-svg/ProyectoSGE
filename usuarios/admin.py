"""APP: usuarios - Admin"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Panel admin personalizado para el modelo Usuario."""
    list_display = ['username', 'get_full_name', 'email', 'rol', 'rut', 'is_active']
    list_filter = ['rol', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'rut', 'email']
    ordering = ['rol', 'last_name']

    # Agregar campos personalizados al formulario de admin
    fieldsets = UserAdmin.fieldsets + (
        ('Datos del Colegio', {
            'fields': ('rol', 'rut', 'telefono', 'foto_perfil')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos del Colegio', {
            'fields': ('rol', 'rut', 'telefono', 'first_name', 'last_name', 'email')
        }),
    )
