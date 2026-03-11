"""
APP: anotaciones
ARCHIVO: models.py

Sistema de anotaciones (observaciones) positivas y negativas.
Las anotaciones quedan registradas en la hoja de vida del alumno.

Relaciones:
    Anotacion -> Alumno (ForeignKey)
    Anotacion -> Asignatura (ForeignKey, opcional - puede ser una anotación general)
    Anotacion -> creado_por/Usuario (ForeignKey)
"""
from django.db import models
from django.utils import timezone


class Anotacion(models.Model):
    """
    Anotación o registro conductual del alumno.
    Puede ser positiva (felicitación, reconocimiento) o
    negativa (llamado de atención, incidente).
    """

    POSITIVA = 'positiva'
    NEGATIVA = 'negativa'
    NEUTRAL = 'neutral'

    TIPOS = [
        (POSITIVA, 'Positiva'),
        (NEGATIVA, 'Negativa'),
        (NEUTRAL, 'Neutral / Informativa'),
    ]

    # Categorías de anotaciones negativas
    CATEGORIAS_NEGATIVAS = [
        ('atraso', 'Atraso'),
        ('conducta', 'Conducta inadecuada'),
        ('material', 'Sin material'),
        ('tarea', 'Sin tarea'),
        ('uniforme', 'Sin uniforme'),
        ('falta_grave', 'Falta grave'),
        ('otro', 'Otro'),
    ]

    # Categorías de anotaciones positivas
    CATEGORIAS_POSITIVAS = [
        ('destacado', 'Rendimiento destacado'),
        ('ayuda', 'Ayuda a compañeros'),
        ('liderazgo', 'Liderazgo positivo'),
        ('actitud', 'Actitud ejemplar'),
        ('logro', 'Logro académico'),
        ('otro', 'Otro'),
    ]

    alumno = models.ForeignKey(
        'alumnos.Alumno',
        on_delete=models.CASCADE,
        related_name='anotaciones',
        verbose_name='Alumno'
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        verbose_name='Tipo'
    )

    categoria = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Categoría'
    )

    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Describe el comportamiento o situación observada'
    )

    fecha = models.DateField(
        default=timezone.now,
        verbose_name='Fecha'
    )

    # Asignatura opcional (si la anotación ocurrió en una clase específica)
    asignatura = models.ForeignKey(
        'asignaturas.Asignatura',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anotaciones',
        verbose_name='Asignatura (opcional)'
    )

    # Quién realizó la anotación
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='anotaciones_creadas',
        verbose_name='Creado por'
    )

    # Firma del apoderado (puede quedar pendiente)
    firmado_por_apoderado = models.BooleanField(
        default=False,
        verbose_name='Firmado por apoderado'
    )

    fecha_firma = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de firma'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anotación'
        verbose_name_plural = 'Anotaciones'
        ordering = ['-fecha', 'alumno__usuario__last_name']

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.alumno.nombre_completo} - {self.fecha}"

    @property
    def es_positiva(self):
        return self.tipo == self.POSITIVA

    @property
    def es_negativa(self):
        return self.tipo == self.NEGATIVA
