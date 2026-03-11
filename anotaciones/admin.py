from django.contrib import admin
from .models import Anotacion
@admin.register(Anotacion)
class AnotacionAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'tipo', 'categoria', 'fecha', 'creado_por', 'firmado_por_apoderado']
    list_filter = ['tipo', 'firmado_por_apoderado', 'fecha']
    search_fields = ['alumno__usuario__last_name', 'descripcion']
