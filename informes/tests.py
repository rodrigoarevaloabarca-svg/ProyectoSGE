import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cursos.models import Curso, NivelEducacional
from alumnos.models import Alumno
from apoderados.models import Apoderado
from informes.models import Periodo

Usuario = get_user_model()


def _make_periodo():
    return Periodo.objects.create(
        tipo='semestre', numero=1, anio=2026,
        fecha_inicio=datetime.date(2026, 3, 1),
        fecha_fin=datetime.date(2026, 6, 30),
    )


class InformesAccesoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nivel = NivelEducacional.objects.create(nombre='Básica', tipo='basica')
        self.curso = Curso.objects.create(nivel=self.nivel, grado=3, letra='A', anio_academico=2026)

        self.u_admin = Usuario.objects.create_user(
            username='inf_admin', password='admin12345678', rol='admin'
        )
        self.u_prof = Usuario.objects.create_user(
            username='inf_prof', password='prof12345678', rol='profesor'
        )
        from profesores.models import Profesor
        self.profesor = Profesor.objects.create(usuario=self.u_prof)

        self.u_alumno = Usuario.objects.create_user(
            username='inf_alumno', password='alum12345678', rol='alumno'
        )
        self.alumno = Alumno.objects.create(
            usuario=self.u_alumno, curso=self.curso, numero_matricula='INF001'
        )
        self.u_apoderado = Usuario.objects.create_user(
            username='inf_apod', password='apod12345678', rol='apoderado'
        )
        self.apoderado = Apoderado.objects.create(usuario=self.u_apoderado)
        self.apoderado.pupilos.add(self.alumno)

        self.periodo = _make_periodo()

    def test_admin_puede_seleccionar_informe(self):
        self.client.force_login(self.u_admin)
        response = self.client.get(reverse('informes:seleccionar'))
        self.assertEqual(response.status_code, 200)

    def test_alumno_no_puede_seleccionar_informe(self):
        self.client.force_login(self.u_alumno)
        response = self.client.get(reverse('informes:seleccionar'))
        self.assertIn(response.status_code, [302, 403])

    def test_admin_puede_ver_informe(self):
        self.client.force_login(self.u_admin)
        response = self.client.get(
            reverse('informes:ver_informe', kwargs={
                'alumno_id': self.alumno.pk,
                'periodo_id': self.periodo.pk,
            })
        )
        self.assertEqual(response.status_code, 200)

    def test_profesor_sin_asignatura_no_puede_ver_informe_ajeno(self):
        self.client.force_login(self.u_prof)
        response = self.client.get(
            reverse('informes:ver_informe', kwargs={
                'alumno_id': self.alumno.pk,
                'periodo_id': self.periodo.pk,
            })
        )
        self.assertRedirects(response, reverse('informes:seleccionar'))

    def test_apoderado_no_puede_ver_informe(self):
        self.client.force_login(self.u_apoderado)
        response = self.client.get(
            reverse('informes:ver_informe', kwargs={
                'alumno_id': self.alumno.pk,
                'periodo_id': self.periodo.pk,
            })
        )
        self.assertIn(response.status_code, [302, 403])
