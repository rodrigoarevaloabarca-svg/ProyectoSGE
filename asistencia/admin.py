from django.contrib import admin
from .models import RegistroAsistencia
@admin.register(RegistroAsistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'asignatura', 'fecha', 'estado']
    list_filter = ['estado', 'fecha', 'asignatura__curso']
    date_hierarchy = 'fecha'
