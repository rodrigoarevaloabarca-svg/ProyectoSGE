from django.test import TestCase
from django.contrib.auth import get_user_model
from alumnos.models import Alumno
from asignaturas.models import Asignatura
from cursos.models import Curso, NivelEducacional
from .models import Nota, TipoEvaluacion, PromedioAsignatura

Usuario = get_user_model()


class PromedioSignalTest(TestCase):
    def setUp(self):
        self.nivel = NivelEducacional.objects.create(nombre='Básica', tipo='basica')
        self.curso = Curso.objects.create(nivel=self.nivel, grado=5, letra='A', anio_academico=2026)
        self.u_alumno = Usuario.objects.create_user(
            username='alumno1', password='alumno12345678', rol='alumno'
        )
        self.alumno = Alumno.objects.create(
            usuario=self.u_alumno, curso=self.curso, numero_matricula='MAT001'
        )
        self.u_prof = Usuario.objects.create_user(
            username='prof1', password='prof12345678', rol='profesor'
        )
        from profesores.models import Profesor
        self.profesor = Profesor.objects.create(usuario=self.u_prof)
        self.asignatura = Asignatura.objects.create(
            nombre='Matemáticas', curso=self.curso, profesor=self.profesor
        )
        self.tipo = TipoEvaluacion.objects.create(nombre='Prueba')

    def test_promedio_se_crea_al_guardar_nota(self):
        Nota.objects.create(
            alumno=self.alumno, asignatura=self.asignatura,
            tipo_evaluacion=self.tipo, valor=6.0, ingresado_por=self.u_prof
        )
        prom = PromedioAsignatura.objects.get(alumno=self.alumno, asignatura=self.asignatura)
        self.assertEqual(float(prom.promedio), 6.0)

    def test_promedio_se_actualiza_al_agregar_nota(self):
        Nota.objects.create(
            alumno=self.alumno, asignatura=self.asignatura,
            tipo_evaluacion=self.tipo, valor=6.0, ingresado_por=self.u_prof
        )
        Nota.objects.create(
            alumno=self.alumno, asignatura=self.asignatura,
            tipo_evaluacion=self.tipo, valor=4.0, ingresado_por=self.u_prof,
            descripcion='Segunda nota'
        )
        prom = PromedioAsignatura.objects.get(alumno=self.alumno, asignatura=self.asignatura)
        self.assertEqual(float(prom.promedio), 5.0)

    def test_nota_fuera_de_rango_falla(self):
        from django.core.exceptions import ValidationError
        nota = Nota(
            alumno=self.alumno, asignatura=self.asignatura,
            tipo_evaluacion=self.tipo, valor=8.0, ingresado_por=self.u_prof
        )
        with self.assertRaises(ValidationError):
            nota.full_clean()

    def test_nota_minima_valida(self):
        nota = Nota(
            alumno=self.alumno, asignatura=self.asignatura,
            tipo_evaluacion=self.tipo, valor=1.0, ingresado_por=self.u_prof
        )
        nota.full_clean()  # no debe lanzar

    def test_promedio_se_elimina_al_borrar_todas_notas(self):
        n = Nota.objects.create(
            alumno=self.alumno, asignatura=self.asignatura,
            tipo_evaluacion=self.tipo, valor=5.0, ingresado_por=self.u_prof
        )
        n.delete()
        prom = PromedioAsignatura.objects.get(alumno=self.alumno, asignatura=self.asignatura)
        self.assertIsNone(prom.promedio)
        self.assertEqual(prom.cantidad_notas, 0)
