from django.contrib import admin
from .models import Nota, TipoEvaluacion, PromedioAsignatura
@admin.register(TipoEvaluacion)
class TipoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'porcentaje_ponderacion']
@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'asignatura', 'tipo_evaluacion', 'valor', 'fecha', 'aprobado']
    list_filter = ['tipo_evaluacion', 'fecha']
    search_fields = ['alumno__usuario__last_name', 'asignatura__nombre']
@admin.register(PromedioAsignatura)
class PromedioAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'asignatura', 'promedio', 'cantidad_notas', 'ultima_actualizacion']
    readonly_fields = ['ultima_actualizacion']
