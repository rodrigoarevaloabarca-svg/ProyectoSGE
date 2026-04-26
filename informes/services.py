"""
Servicio de recopilación de datos para informes académicos.
Centraliza la lógica de negocio separándola de las vistas HTTP.
"""
from anotaciones.models import Anotacion
from asistencia.models import RegistroAsistencia
from notas.models import Nota


class InformeService:
    @staticmethod
    def recopilar_datos(alumno, periodo):
        """
        Recopila notas, asistencia y anotaciones del alumno en el período dado.
        Retorna un dict listo para pasar a la vista o al generador de PDF.
        """
        fecha_i = periodo.fecha_inicio
        fecha_f = periodo.fecha_fin

        # Notas del período agrupadas por asignatura
        notas_qs = Nota.objects.filter(
            alumno=alumno,
            fecha__gte=fecha_i,
            fecha__lte=fecha_f,
        ).select_related('asignatura', 'tipo_evaluacion').order_by('asignatura__nombre', 'fecha')

        notas_por_asignatura = {}
        for nota in notas_qs:
            nombre_asig = nota.asignatura.nombre
            if nombre_asig not in notas_por_asignatura:
                notas_por_asignatura[nombre_asig] = {
                    'asignatura': nota.asignatura,
                    'notas': [],
                    'promedio': None,
                }
            notas_por_asignatura[nombre_asig]['notas'].append(nota)

        for data in notas_por_asignatura.values():
            valores = [float(n.valor) for n in data['notas']]
            data['promedio'] = round(sum(valores) / len(valores), 1) if valores else None

        todos_promedios = [d['promedio'] for d in notas_por_asignatura.values() if d['promedio']]
        promedio_general = round(sum(todos_promedios) / len(todos_promedios), 1) if todos_promedios else None

        # Asistencia del período
        asistencias   = RegistroAsistencia.objects.filter(alumno=alumno, fecha__gte=fecha_i, fecha__lte=fecha_f)
        total_clases  = asistencias.count()
        presentes     = asistencias.filter(estado='presente').count()
        ausentes      = asistencias.filter(estado='ausente').count()
        atrasados     = asistencias.filter(estado='atrasado').count()
        justificados  = asistencias.filter(estado='justificado').count()
        pct_asistencia = round((presentes / total_clases * 100), 1) if total_clases > 0 else 0

        # Anotaciones del período
        anotaciones = Anotacion.objects.filter(
            alumno=alumno, fecha__gte=fecha_i, fecha__lte=fecha_f,
        ).select_related('creado_por', 'asignatura').order_by('fecha')

        return {
            'notas_por_asignatura': notas_por_asignatura,
            'promedio_general':     promedio_general,
            'asistencia': {
                'total':        total_clases,
                'presentes':    presentes,
                'ausentes':     ausentes,
                'atrasados':    atrasados,
                'justificados': justificados,
                'porcentaje':   pct_asistencia,
            },
            'anotaciones': anotaciones,
            'positivas':   anotaciones.filter(tipo='positiva'),
            'negativas':   anotaciones.filter(tipo='negativa'),
        }
