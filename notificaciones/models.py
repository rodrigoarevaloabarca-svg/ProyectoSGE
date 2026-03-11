"""
APP: notificaciones
ARCHIVO: models.py
"""
from django.db import models
from django.utils import timezone


class Notificacion(models.Model):

    TIPO_CHOICES = [
        ('mensaje',   'Mensaje libre'),
        ('masivo',    'Envío masivo'),
    ]

    remitente    = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.CASCADE,
        related_name='notificaciones_enviadas'
    )
    destinatario = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.CASCADE,
        related_name='notificaciones_recibidas',
        null=True, blank=True   # null en envíos masivos (se crean N registros individuales)
    )
    titulo       = models.CharField(max_length=200)
    mensaje      = models.TextField()
    tipo         = models.CharField(max_length=20, choices=TIPO_CHOICES, default='mensaje')
    leida        = models.BooleanField(default=False)
    fecha_envio  = models.DateTimeField(default=timezone.now)
    fecha_leida  = models.DateTimeField(null=True, blank=True)

    # Para rastrear si se envió también por email
    enviada_por_email = models.BooleanField(default=False)

    # Referencia opcional al envío masivo padre
    envio_masivo = models.ForeignKey(
        'EnvioMasivo', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notificaciones'
    )

    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.titulo} → {self.destinatario}"

    def marcar_leida(self):
        if not self.leida:
            self.leida       = True
            self.fecha_leida = timezone.now()
            self.save(update_fields=['leida', 'fecha_leida'])


class EnvioMasivo(models.Model):
    """Registro de cada envío masivo para tener historial."""

    DESTINO_CHOICES = [
        ('todos_apoderados',  'Todos los apoderados'),
        ('todos_profesores',  'Todos los profesores'),
        ('todos',             'Apoderados y profesores'),
        ('curso_apoderados',  'Apoderados de un curso'),
    ]

    remitente      = models.ForeignKey(
        'usuarios.Usuario', on_delete=models.CASCADE,
        related_name='envios_masivos'
    )
    titulo         = models.CharField(max_length=200)
    mensaje        = models.TextField()
    destino        = models.CharField(max_length=30, choices=DESTINO_CHOICES)
    curso          = models.ForeignKey(
        'cursos.Curso', on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Solo si destino es apoderados de un curso'
    )
    fecha_envio    = models.DateTimeField(default=timezone.now)
    total_enviados = models.PositiveIntegerField(default=0)
    enviado_email  = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = 'Envío Masivo'
        verbose_name_plural = 'Envíos Masivos'

    def __str__(self):
        return f"[{self.get_destino_display()}] {self.titulo} — {self.fecha_envio:%d/%m/%Y}"
