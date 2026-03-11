"""
APP: asistencia
ARCHIVO: models.py

Sistema de registro de asistencia diaria por asignatura.

Relaciones:
    RegistroAsistencia -> Alumno (ForeignKey)
    RegistroAsistencia -> Asignatura (ForeignKey)
    RegistroAsistencia -> registrado_por/Usuario (ForeignKey)
"""
from django.db import models
from django.utils import timezone


class RegistroAsistencia(models.Model):
    """
    Un registro de asistencia = un alumno en una clase específica en una fecha.
    
    Estado puede ser: presente, ausente, atrasado, justificado
    """

    PRESENTE = 'presente'
    AUSENTE = 'ausente'
    ATRASADO = 'atrasado'
    JUSTIFICADO = 'justificado'

    ESTADOS = [
        (PRESENTE, 'Presente'),
        (AUSENTE, 'Ausente'),
        (ATRASADO, 'Atrasado'),
        (JUSTIFICADO, 'Justificado'),
    ]

    alumno = models.ForeignKey(
        'alumnos.Alumno',
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name='Alumno'
    )

    asignatura = models.ForeignKey(
        'asignaturas.Asignatura',
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name='Asignatura'
    )

    fecha = models.DateField(
        default=timezone.now,
        verbose_name='Fecha'
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default=PRESENTE,
        verbose_name='Estado'
    )

    observacion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observación',
        help_text='Ej: Certificado médico presentado'
    )

    registrado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asistencias_registradas',
        verbose_name='Registrado por'
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Asistencia'
        verbose_name_plural = 'Registros de Asistencia'
        # No puede haber dos registros del mismo alumno en la misma asignatura y fecha
        unique_together = ['alumno', 'asignatura', 'fecha']
        ordering = ['-fecha', 'alumno__usuario__last_name']

    def __str__(self):
        return f"{self.alumno.nombre_completo} - {self.asignatura.nombre} - {self.fecha}: {self.get_estado_display()}"

    @classmethod
    def tomar_asistencia_curso(cls, asignatura, fecha, datos_asistencia, profesor):
        """
        Toma la asistencia de un curso completo en una sola operación.
        
        datos_asistencia: lista de dicts [{'alumno_id': 1, 'estado': 'presente'}, ...]
        
        Usa bulk_create para eficiencia (una sola query a la BD).
        """
        registros_a_crear = []
        registros_a_actualizar = []

        for dato in datos_asistencia:
            alumno_id = dato['alumno_id']
            estado = dato['estado']

            # Verificar si ya existe un registro para hoy
            registro_existente = cls.objects.filter(
                alumno_id=alumno_id,
                asignatura=asignatura,
                fecha=fecha
            ).first()

            if registro_existente:
                registro_existente.estado = estado
                registro_existente.registrado_por = profesor
                registros_a_actualizar.append(registro_existente)
            else:
                registros_a_crear.append(cls(
                    alumno_id=alumno_id,
                    asignatura=asignatura,
                    fecha=fecha,
                    estado=estado,
                    registrado_por=profesor
                ))

        # Operaciones en bulk para eficiencia
        if registros_a_crear:
            cls.objects.bulk_create(registros_a_crear)
        if registros_a_actualizar:
            cls.objects.bulk_update(registros_a_actualizar, ['estado', 'registrado_por'])

        return len(registros_a_crear) + len(registros_a_actualizar)
