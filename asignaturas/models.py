"""
APP: asignaturas
ARCHIVO: models.py

Asignatura: materia que se dicta en un curso específico por un profesor.

Relaciones:
    Asignatura -> Curso (ForeignKey): pertenece a un curso
    Asignatura -> Profesor (ForeignKey): es dictada por un profesor
    Asignatura <- Nota (ForeignKey desde Nota)
    Asignatura <- RegistroAsistencia (ForeignKey desde RegistroAsistencia)
"""
from django.db import models


class Asignatura(models.Model):
    """
    Una asignatura = una materia dictada en un curso por un profesor.
    Ejemplo: 'Matemáticas - 3° Básico A - Prof. García'
    """

    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre de la asignatura'
    )

    # ForeignKey: muchas asignaturas pertenecen a un curso
    curso = models.ForeignKey(
        'cursos.Curso',
        on_delete=models.CASCADE,
        related_name='asignaturas',
        verbose_name='Curso'
    )

    # ForeignKey: muchas asignaturas puede dictar un profesor
    profesor = models.ForeignKey(
        'profesores.Profesor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asignaturas',
        verbose_name='Profesor'
    )

    # Horas semanales (útil para reportes)
    horas_semanales = models.PositiveSmallIntegerField(
        default=2,
        verbose_name='Horas semanales'
    )

    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'
        # Una asignatura es única por nombre + curso (no puede repetirse)
        unique_together = ['nombre', 'curso']
        ordering = ['curso', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.curso}"

    def get_promedio(self):
        """Promedio general de la asignatura (todos los alumnos del curso)."""
        notas = self.notas.values_list('valor', flat=True)
        if notas:
            return round(sum(notas) / len(notas), 1)
        return None

    def get_notas_alumno(self, alumno):
        """Retorna todas las notas de un alumno específico en esta asignatura."""
        return self.notas.filter(alumno=alumno).order_by('tipo_evaluacion', 'fecha')

    def get_promedio_alumno(self, alumno):
        """Calcula el promedio de un alumno específico en esta asignatura."""
        notas = self.notas.filter(alumno=alumno).values_list('valor', flat=True)
        if notas:
            return round(sum(notas) / len(notas), 1)
        return None
