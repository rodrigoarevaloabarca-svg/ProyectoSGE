from django.contrib import admin
from .models import Apoderado
@admin.register(Apoderado)
class ApoderadoAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'parentesco', 'activo']
    search_fields = ['usuario__first_name', 'usuario__last_name']
