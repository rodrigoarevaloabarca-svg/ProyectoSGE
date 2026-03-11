from django.contrib import admin
from .models import Profesor
@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'especialidad', 'activo']
    search_fields = ['usuario__first_name', 'usuario__last_name']
