"""
APP: historial
ARCHIVO: models.py

Registro de auditoría para cambios en Notas y Anotaciones.
Guarda un snapshot del estado anterior y posterior a cada modificación.
"""
from django.db import models
from django.utils import timezone


class HistorialCambio(models.Model):

    MODELO_NOTA      = 'nota'
    MODELO_ANOTACION = 'anotacion'

    MODELOS = [
        (MODELO_NOTA,      'Nota'),
        (MODELO_ANOTACION, 'Anotación'),
    ]

    ACCION_EDICION    = 'edicion'
    ACCION_ELIMINACION = 'eliminacion'

    ACCIONES = [
        (ACCION_EDICION,     'Edición'),
        (ACCION_ELIMINACION, 'Eliminación'),
    ]

    modelo = models.CharField(
        max_length=20,
        choices=MODELOS,
        verbose_name='Módulo'
    )

    objeto_id = models.PositiveIntegerField(
        verbose_name='ID del registro modificado'
    )

    accion = models.CharField(
        max_length=20,
        choices=ACCIONES,
        default=ACCION_EDICION,
        verbose_name='Acción'
    )

    modificado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='historial_cambios',
        verbose_name='Modificado por'
    )

    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha y hora'
    )

    # Descripción legible del objeto afectado (ej: "Nota de Juan Pérez - Matemáticas")
    descripcion_objeto = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Objeto afectado'
    )

    datos_antes = models.JSONField(
        verbose_name='Estado anterior'
    )

    datos_despues = models.JSONField(
        verbose_name='Estado posterior',
        null=True,
        blank=True  # null en caso de eliminación
    )

    class Meta:
        verbose_name        = 'Historial de Cambio'
        verbose_name_plural = 'Historial de Cambios'
        ordering            = ['-fecha']

    def __str__(self):
        return f"[{self.get_modelo_display()}] {self.get_accion_display()} por {self.modificado_por} — {self.fecha:%d/%m/%Y %H:%M}"
