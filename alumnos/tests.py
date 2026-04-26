from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from alumnos.models import Alumno
from apoderados.models import Apoderado
from cursos.models import Curso, NivelEducacional

Usuario = get_user_model()


class AlumnoIDORTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nivel = NivelEducacional.objects.create(nombre='Básica', tipo='basica')
        self.curso = Curso.objects.create(nivel=self.nivel, grado=7, letra='A', anio_academico=2026)

        self.u_admin = Usuario.objects.create_user(
            username='al_admin', password='admin12345678', rol='admin'
        )
        self.u_alumno1 = Usuario.objects.create_user(
            username='al_alumno1', password='alum12345678', rol='alumno'
        )
        self.alumno1 = Alumno.objects.create(
            usuario=self.u_alumno1, curso=self.curso, numero_matricula='A001'
        )
        self.u_alumno2 = Usuario.objects.create_user(
            username='al_alumno2', password='alum12345678', rol='alumno'
        )
        self.alumno2 = Alumno.objects.create(
            usuario=self.u_alumno2, curso=self.curso, numero_matricula='A002'
        )
        self.u_apoderado = Usuario.objects.create_user(
            username='al_apod', password='apod12345678', rol='apoderado'
        )
        self.apoderado = Apoderado.objects.create(usuario=self.u_apoderado)
        self.apoderado.pupilos.add(self.alumno1)

    def test_alumno_puede_ver_su_propio_detalle(self):
        self.client.force_login(self.u_alumno1)
        response = self.client.get(reverse('alumnos:detalle', kwargs={'pk': self.alumno1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_alumno_no_puede_ver_detalle_ajeno(self):
        self.client.force_login(self.u_alumno1)
        response = self.client.get(reverse('alumnos:detalle', kwargs={'pk': self.alumno2.pk}))
        self.assertRedirects(response, reverse('dashboard:inicio'))

    def test_apoderado_puede_ver_su_pupilo(self):
        self.client.force_login(self.u_apoderado)
        response = self.client.get(reverse('alumnos:detalle', kwargs={'pk': self.alumno1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_apoderado_no_puede_ver_alumno_ajeno(self):
        self.client.force_login(self.u_apoderado)
        response = self.client.get(reverse('alumnos:detalle', kwargs={'pk': self.alumno2.pk}))
        self.assertRedirects(response, reverse('dashboard:inicio'))

    def test_admin_puede_ver_cualquier_alumno(self):
        self.client.force_login(self.u_admin)
        response = self.client.get(reverse('alumnos:detalle', kwargs={'pk': self.alumno2.pk}))
        self.assertEqual(response.status_code, 200)
