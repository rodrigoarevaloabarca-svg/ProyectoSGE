"""
APP: apoderados
ARCHIVO: models.py

Modelo Apoderado: representante legal del alumno.
Un apoderado puede tener varios pupilos (alumnos).
"""
from django.db import models


class Apoderado(models.Model):
    """Perfil del apoderado/tutor legal del alumno."""

    usuario = models.OneToOneField(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='perfil_apoderado',
        verbose_name='Usuario'
    )

    # Relación con el alumno: uno a muchos (un apoderado puede tener varios hijos)
    # Esta relación se define en Alumno con ForeignKey a Apoderado

    parentesco = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Parentesco',
        help_text='Ej: Padre, Madre, Tutor legal'
    )

    ocupacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ocupación'
    )

    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Apoderado'
        verbose_name_plural = 'Apoderados'
        ordering = ['usuario__last_name', 'usuario__first_name']

    def __str__(self):
        return f"{self.usuario.get_full_name()} (Apoderado)"

    @property
    def nombre_completo(self):
        return self.usuario.get_full_name()

    def get_pupilos(self):
        """Retorna todos los alumnos que tutela."""
        return self.pupilos.all()
