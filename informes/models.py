"""
APP: informes
ARCHIVO: models.py

Sistema de períodos académicos e informes por alumno.
Soporta trimestres y semestres con año escolar chileno (Marzo-Diciembre).
"""
from django.db import models
from django.utils import timezone


class Periodo(models.Model):
    """
    Período académico: trimestre o semestre.
    Año escolar chileno: Marzo - Diciembre
    """
    TRIMESTRE = 'trimestre'
    SEMESTRE  = 'semestre'
    TIPOS = [
        (TRIMESTRE, 'Trimestre'),
        (SEMESTRE,  'Semestre'),
    ]

    # Períodos predefinidos por tipo
    # Semestres:  1=Mar-Jun, 2=Jul-Dic
    # Trimestres: 1=Mar-May, 2=Jun-Ago, 3=Sep-Dic
    NUMEROS_SEMESTRE  = [(1,'1° Semestre'), (2,'2° Semestre')]
    NUMEROS_TRIMESTRE = [(1,'1° Trimestre'), (2,'2° Trimestre'), (3,'3° Trimestre')]

    tipo    = models.CharField(max_length=10, choices=TIPOS, verbose_name='Tipo')
    numero  = models.PositiveSmallIntegerField(verbose_name='Número')
    anio    = models.PositiveSmallIntegerField(verbose_name='Año', default=timezone.now().year)
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin    = models.DateField(verbose_name='Fecha de término')
    activo  = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Período'
        verbose_name_plural = 'Períodos'
        ordering = ['-anio', 'tipo', 'numero']
        unique_together = ['tipo', 'numero', 'anio']

    def __str__(self):
        return f"{self.get_numero_display()} {self.anio}"

    def get_numero_display(self):
        if self.tipo == self.SEMESTRE:
            nums = dict(self.NUMEROS_SEMESTRE)
        else:
            nums = dict(self.NUMEROS_TRIMESTRE)
        return nums.get(self.numero, f'N°{self.numero}')

    @classmethod
    def crear_periodo_automatico(cls, tipo, numero, anio):
        """Crea un período con fechas automáticas según el año escolar chileno."""
        if tipo == cls.SEMESTRE:
            fechas = {
                1: ('03-01', '06-30'),
                2: ('07-01', '12-15'),
            }
        else:  # trimestre
            fechas = {
                1: ('03-01', '05-31'),
                2: ('06-01', '08-31'),
                3: ('09-01', '12-15'),
            }
        inicio_str, fin_str = fechas[numero]
        return cls.objects.create(
            tipo=tipo, numero=numero, anio=anio,
            fecha_inicio=f'{anio}-{inicio_str.replace("-", "-")}',
            fecha_fin=f'{anio}-{fin_str.replace("-", "-")}',
        )


class ComentarioInforme(models.Model):
    """
    Comentario del profesor para el informe de un alumno en un período.
    """
    alumno  = models.ForeignKey('alumnos.Alumno',  on_delete=models.CASCADE, related_name='comentarios_informe')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='comentarios')
    profesor = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, related_name='comentarios_emitidos')
    comentario = models.TextField(blank=True, verbose_name='Comentario del profesor')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comentario de Informe'
        unique_together = ['alumno', 'periodo']
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Informe {self.alumno} - {self.periodo}"
