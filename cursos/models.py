"""
APP: cursos
ARCHIVO: models.py

Modelos para la estructura de cursos del sistema educacional chileno.
Niveles: 1° a 8° Básico, 1° a 4° Medio
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class NivelEducacional(models.Model):
    """
    Representa el nivel educacional: Básica o Media.
    Ejemplo: 'Educación Básica', 'Educación Media'
    """
    BASICA = 'basica'
    MEDIA = 'media'

    TIPOS = [
        (BASICA, 'Educación Básica'),
        (MEDIA, 'Educación Media'),
    ]

    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    tipo = models.CharField(max_length=10, choices=TIPOS, unique=True)

    class Meta:
        verbose_name = 'Nivel Educacional'
        verbose_name_plural = 'Niveles Educacionales'

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    """
    Un curso específico: ej. '3° Básico A', '1° Medio B'
    
    Relaciones:
    - nivel: ForeignKey a NivelEducacional
    - profesor_jefe: ForeignKey a Profesor (nullable, un curso puede no tener jefe aún)
    - alumnos: se accede vía alumno.curso (OneToOne desde Alumno)
    - asignaturas: ManyToMany con Asignatura
    """
    nivel = models.ForeignKey(
        NivelEducacional,
        on_delete=models.PROTECT,  # No borrar nivel si tiene cursos
        verbose_name='Nivel',
        related_name='cursos'
    )

    # Grado: 1-8 para básica, 1-4 para media
    grado = models.PositiveSmallIntegerField(
        verbose_name='Grado',
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        help_text='1-8 para básica, 1-4 para media'
    )

    # Letra del curso: A, B, C...
    letra = models.CharField(
        max_length=1,
        verbose_name='Letra',
        help_text='Ej: A, B, C'
    )

    anio_academico = models.PositiveSmallIntegerField(
        verbose_name='Año académico',
        help_text='Ej: 2024'
    )

    # Profesor jefe puede no estar asignado aún
    profesor_jefe = models.ForeignKey(
        'profesores.Profesor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Profesor jefe',
        related_name='cursos_como_jefe'
    )

    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        # Un curso es único por grado + letra + año
        unique_together = ['nivel', 'grado', 'letra', 'anio_academico']
        ordering = ['anio_academico', 'nivel', 'grado', 'letra']

    def __str__(self):
        tipo = 'Básico' if self.nivel.tipo == 'basica' else 'Medio'
        return f"{self.grado}° {tipo} {self.letra} ({self.anio_academico})"

    @property
    def nombre_completo(self):
        return str(self)

    def get_promedio_curso(self):
        """Calcula el promedio general del curso en todas las asignaturas."""
        from notas.models import Nota
        notas = Nota.objects.filter(
            alumno__curso=self
        ).values_list('valor', flat=True)
        if notas:
            return round(sum(notas) / len(notas), 1)
        return None

    def get_porcentaje_asistencia(self):
        """Calcula el porcentaje promedio de asistencia del curso."""
        from asistencia.models import RegistroAsistencia
        registros = RegistroAsistencia.objects.filter(alumno__curso=self)
        if not registros.exists():
            return None
        presentes = registros.filter(estado='presente').count()
        return round((presentes / registros.count()) * 100, 1)
