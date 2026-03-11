from django.contrib import admin
from .models import Alumno
@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ['numero_matricula', 'nombre_completo', 'curso', 'activo']
    list_filter = ['curso__nivel', 'activo']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'numero_matricula', 'usuario__rut']
    raw_id_fields = ['usuario', 'apoderado']
