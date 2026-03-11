from django.contrib import admin
from .models import Curso, NivelEducacional
@admin.register(NivelEducacional)
class NivelAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo']
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'nivel', 'grado', 'letra', 'anio_academico', 'profesor_jefe', 'activo']
    list_filter = ['nivel', 'anio_academico', 'activo']
