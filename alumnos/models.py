"""
APP: alumnos
ARCHIVO: models.py

Modelo Alumno: vincula un Usuario con un Curso y un Apoderado.
El alumno es la entidad central del sistema.

Relaciones:
    Alumno -> Usuario (OneToOne): cada alumno ES un usuario del sistema
    Alumno -> Curso (ForeignKey): alumno pertenece a un curso
    Alumno -> Apoderado (ForeignKey): alumno tiene un apoderado responsable
"""
from django.db import models
from django.core.validators import RegexValidator


class Alumno(models.Model):
    """
    Perfil extendido del alumno.
    Separado del Usuario para mantener datos académicos independientes.
    """

    # OneToOneField: un usuario = un alumno máximo
    usuario = models.OneToOneField(
        'usuarios.Usuario',
        on_delete=models.CASCADE,  # Si se elimina el usuario, se elimina el alumno
        related_name='perfil_alumno',
        verbose_name='Usuario'
    )

    # ForeignKey: muchos alumnos pertenecen a un curso
    curso = models.ForeignKey(
        'cursos.Curso',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alumnos',
        verbose_name='Curso'
    )

    # ForeignKey: un apoderado puede tener varios alumnos
    apoderado = models.ForeignKey(
        'apoderados.Apoderado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pupilos',
        verbose_name='Apoderado'
    )

    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de nacimiento',
        null=True,
        blank=True
    )

    fecha_matricula = models.DateField(
        verbose_name='Fecha de matrícula',
        auto_now_add=True
    )

    # Número de matrícula único del colegio
    numero_matricula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='N° Matrícula'
    )

    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )

    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['usuario__last_name', 'usuario__first_name']

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.curso}"

    @property
    def nombre_completo(self):
        return self.usuario.get_full_name()

    @property
    def rut(self):
        return self.usuario.rut

    def get_promedio_general(self):
        """
        Calcula el promedio general del alumno en todas sus asignaturas.
        Retorna None si no hay notas.
        """
        from notas.models import Nota
        notas = Nota.objects.filter(alumno=self).values_list('valor', flat=True)
        if notas:
            return round(sum(notas) / len(notas), 1)
        return None

    def get_promedio_por_asignatura(self):
        """
        Retorna un diccionario {asignatura: promedio} para el alumno.
        Útil para mostrar el libro de notas.
        """
        from notas.models import Nota
        from asignaturas.models import Asignatura

        resultado = {}
        asignaturas = Asignatura.objects.filter(curso=self.curso)

        for asig in asignaturas:
            notas = Nota.objects.filter(alumno=self, asignatura=asig)
            if notas.exists():
                valores = notas.values_list('valor', flat=True)
                resultado[asig] = round(sum(valores) / len(valores), 1)
            else:
                resultado[asig] = None

        return resultado

    def get_porcentaje_asistencia(self):
        """Calcula el porcentaje de asistencia del alumno."""
        from asistencia.models import RegistroAsistencia
        registros = RegistroAsistencia.objects.filter(alumno=self)
        if not registros.exists():
            return None
        presentes = registros.filter(estado='presente').count()
        return round((presentes / registros.count()) * 100, 1)
