from django.contrib import admin
from .models import Notificacion, EnvioMasivo

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ['titulo', 'remitente', 'destinatario', 'leida', 'fecha_envio']
    list_filter   = ['leida', 'tipo', 'enviada_por_email']
    search_fields = ['titulo', 'mensaje']

@admin.register(EnvioMasivo)
class EnvioMasivoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'remitente', 'destino', 'total_enviados', 'fecha_envio']
    list_filter  = ['destino', 'enviado_email']
