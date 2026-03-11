from django.contrib import admin
from .models import Asignatura
@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'curso', 'profesor', 'horas_semanales', 'activo']
    list_filter = ['curso__nivel', 'activo']
    search_fields = ['nombre']
