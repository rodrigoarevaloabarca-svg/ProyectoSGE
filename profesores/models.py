"""
APP: profesores
ARCHIVO: models.py

Modelo Profesor: vincula un Usuario con su información laboral.
Un profesor puede dictar múltiples asignaturas en múltiples cursos.

Relaciones:
    Profesor -> Usuario (OneToOne)
    Profesor -> Asignatura (a través de AsignaturaProfesor)
    Profesor <- Curso (como profesor_jefe, ForeignKey invertido)
"""
from django.db import models


class Profesor(models.Model):
    """Perfil extendido del docente."""

    usuario = models.OneToOneField(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='perfil_profesor',
        verbose_name='Usuario'
    )

    especialidad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Especialidad / Mención'
    )

    fecha_ingreso = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de ingreso al colegio'
    )

    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
        ordering = ['usuario__last_name', 'usuario__first_name']

    def __str__(self):
        return f"Prof. {self.usuario.get_full_name()}"

    @property
    def nombre_completo(self):
        return self.usuario.get_full_name()

    def get_asignaturas(self):
        """Retorna todas las asignaturas que dicta este profesor."""
        return self.asignaturas.all()

    def get_cursos(self):
        """Retorna todos los cursos donde este profesor dicta clases."""
        from cursos.models import Curso
        return Curso.objects.filter(
            asignaturas__profesor=self
        ).distinct()
