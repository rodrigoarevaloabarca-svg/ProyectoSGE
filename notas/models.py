"""
APP: notas
ARCHIVO: models.py

Sistema de notas con escala chilena (1.0 a 7.0).
Nota de aprobación mínima: 4.0

Relaciones:
    Nota -> Alumno (ForeignKey)
    Nota -> Asignatura (ForeignKey)
    Nota -> creado_por/Usuario (ForeignKey, quién ingresó la nota)
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class TipoEvaluacion(models.Model):
    """
    Tipos de evaluación configurables.
    Ejemplo: Prueba, Tarea, Trabajo, Disertación, Proyecto
    """
    nombre = models.CharField(max_length=50, unique=True)
    porcentaje_ponderacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        help_text='Ponderación en % para el promedio (ej: 60.00 para 60%)'
    )

    class Meta:
        verbose_name = 'Tipo de Evaluación'
        verbose_name_plural = 'Tipos de Evaluación'

    def __str__(self):
        return self.nombre


class Nota(models.Model):
    """
    Registro de una nota individual.
    
    Escala chilena: 1.0 (mínimo) a 7.0 (máximo)
    Nota de aprobación: 4.0
    """

    # ForeignKey: un alumno tiene muchas notas
    alumno = models.ForeignKey(
        'alumnos.Alumno',
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Alumno'
    )

    # ForeignKey: una asignatura tiene muchas notas
    asignatura = models.ForeignKey(
        'asignaturas.Asignatura',
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Asignatura'
    )

    tipo_evaluacion = models.ForeignKey(
        TipoEvaluacion,
        on_delete=models.PROTECT,
        related_name='notas',
        verbose_name='Tipo de evaluación'
    )

    # Escala 1.0 a 7.0 (validación con MinValueValidator y MaxValueValidator)
    valor = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(1.0, message='La nota mínima es 1.0'),
            MaxValueValidator(7.0, message='La nota máxima es 7.0')
        ],
        verbose_name='Nota'
    )

    fecha = models.DateField(
        default=timezone.now,
        verbose_name='Fecha de evaluación'
    )

    descripcion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción',
        help_text='Ej: Prueba Unidad 3, Trabajo grupal...'
    )

    # Auditoría: quién ingresó la nota
    ingresado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='notas_ingresadas',
        verbose_name='Ingresado por'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        ordering = ['alumno', 'asignatura', 'fecha']

    def __str__(self):
        return f"{self.alumno.nombre_completo} - {self.asignatura.nombre}: {self.valor}"

    @property
    def aprobado(self):
        """True si la nota es mayor o igual a 4.0 (nota de aprobación chilena)."""
        return self.valor >= 4.0

    @property
    def valor_display(self):
        """Retorna la nota formateada con un decimal."""
        return f"{self.valor:.1f}"


class PromedioAsignatura(models.Model):
    """
    Tabla de promedios calculados para optimizar consultas frecuentes.
    Se actualiza automáticamente vía signal cuando se guarda una Nota.
    
    Este modelo funciona como caché de promedios.
    """
    alumno = models.ForeignKey(
        'alumnos.Alumno',
        on_delete=models.CASCADE,
        related_name='promedios'
    )
    asignatura = models.ForeignKey(
        'asignaturas.Asignatura',
        on_delete=models.CASCADE,
        related_name='promedios'
    )
    promedio = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True
    )
    cantidad_notas = models.PositiveSmallIntegerField(default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Promedio por Asignatura'
        verbose_name_plural = 'Promedios por Asignatura'
        unique_together = ['alumno', 'asignatura']

    def __str__(self):
        return f"{self.alumno} - {self.asignatura}: {self.promedio}"

    @classmethod
    def recalcular(cls, alumno, asignatura):
        """
        Recalcula y guarda el promedio de un alumno en una asignatura.
        Llamado desde signals.py cuando se crea/edita/elimina una Nota.
        """
        notas = Nota.objects.filter(
            alumno=alumno,
            asignatura=asignatura
        ).values_list('valor', flat=True)

        promedio_obj, created = cls.objects.get_or_create(
            alumno=alumno,
            asignatura=asignatura
        )

        if notas:
            promedio_obj.promedio = round(sum(notas) / len(notas), 1)
            promedio_obj.cantidad_notas = len(notas)
        else:
            promedio_obj.promedio = None
            promedio_obj.cantidad_notas = 0

        promedio_obj.save()
        return promedio_obj
