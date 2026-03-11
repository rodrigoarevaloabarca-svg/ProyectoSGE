from django.contrib import admin
from .models import Periodo, ComentarioInforme

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display  = ['__str__', 'tipo', 'anio', 'fecha_inicio', 'fecha_fin', 'activo']
    list_filter   = ['tipo', 'anio', 'activo']
    list_editable = ['activo']

@admin.register(ComentarioInforme)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'periodo', 'profesor', 'fecha_creacion']
    list_filter  = ['periodo']
