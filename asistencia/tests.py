from django.test import TestCase
from django.contrib.auth import get_user_model
from alumnos.models import Alumno
from asignaturas.models import Asignatura
from cursos.models import Curso, NivelEducacional
from .models import RegistroAsistencia
import datetime

Usuario = get_user_model()


class BulkAsistenciaTest(TestCase):
    def setUp(self):
        self.nivel = NivelEducacional.objects.create(nombre='Básica', tipo='basica')
        self.curso = Curso.objects.create(nivel=self.nivel, grado=6, letra='B', anio_academico=2026)
        self.u_prof = Usuario.objects.create_user(
            username='prof_asist', password='prof12345678', rol='profesor'
        )
        from profesores.models import Profesor
        self.profesor = Profesor.objects.create(usuario=self.u_prof)
        self.asignatura = Asignatura.objects.create(
            nombre='Historia', curso=self.curso, profesor=self.profesor
        )
        # Crear 3 alumnos
        self.alumnos = []
        for i in range(3):
            u = Usuario.objects.create_user(
                username=f'alumno_asist_{i}', password='pass12345678', rol='alumno'
            )
            a = Alumno.objects.create(
                usuario=u, curso=self.curso, numero_matricula=f'AST00{i}'
            )
            self.alumnos.append(a)

    def test_tomar_asistencia_bulk_crea_registros(self):
        fecha = datetime.date(2026, 4, 1)
        datos = [
            {'alumno_id': a.pk, 'estado': 'presente'} for a in self.alumnos
        ]
        with self.assertNumQueries(2):  # 1 select existentes + 1 bulk_create (bulk_update vacío no emite query)
            count = RegistroAsistencia.tomar_asistencia_curso(
                self.asignatura, fecha, datos, self.u_prof
            )
        self.assertEqual(count, 3)
        self.assertEqual(RegistroAsistencia.objects.filter(fecha=fecha).count(), 3)

    def test_tomar_asistencia_actualiza_si_ya_existe(self):
        fecha = datetime.date(2026, 4, 2)
        datos = [{'alumno_id': self.alumnos[0].pk, 'estado': 'presente'}]
        RegistroAsistencia.tomar_asistencia_curso(self.asignatura, fecha, datos, self.u_prof)

        datos_upd = [{'alumno_id': self.alumnos[0].pk, 'estado': 'ausente'}]
        RegistroAsistencia.tomar_asistencia_curso(self.asignatura, fecha, datos_upd, self.u_prof)

        reg = RegistroAsistencia.objects.get(
            alumno=self.alumnos[0], asignatura=self.asignatura, fecha=fecha
        )
        self.assertEqual(reg.estado, 'ausente')
