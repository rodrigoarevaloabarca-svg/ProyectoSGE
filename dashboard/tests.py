from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from cursos.models import Curso, NivelEducacional
from alumnos.models import Alumno
from apoderados.models import Apoderado

Usuario = get_user_model()


class DashboardRolTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.nivel = NivelEducacional.objects.create(nombre='Básica', tipo='basica')
        self.curso = Curso.objects.create(nivel=self.nivel, grado=4, letra='A', anio_academico=2026)

        self.u_admin = Usuario.objects.create_user(
            username='dash_admin', password='admin12345678', rol='admin'
        )
        self.u_prof = Usuario.objects.create_user(
            username='dash_prof', password='prof12345678', rol='profesor'
        )
        from profesores.models import Profesor
        self.profesor = Profesor.objects.create(usuario=self.u_prof)

        self.u_alumno = Usuario.objects.create_user(
            username='dash_alumno', password='alum12345678', rol='alumno'
        )
        self.alumno = Alumno.objects.create(
            usuario=self.u_alumno, curso=self.curso, numero_matricula='D001'
        )
        self.u_apoderado = Usuario.objects.create_user(
            username='dash_apod', password='apod12345678', rol='apoderado'
        )
        self.apoderado = Apoderado.objects.create(usuario=self.u_apoderado)
        self.apoderado.pupilos.add(self.alumno)

    def test_admin_ve_dashboard(self):
        self.client.force_login(self.u_admin)
        response = self.client.get(reverse('dashboard:inicio'))
        self.assertEqual(response.status_code, 200)

    def test_profesor_ve_dashboard(self):
        self.client.force_login(self.u_prof)
        response = self.client.get(reverse('dashboard:inicio'))
        self.assertEqual(response.status_code, 200)

    def test_alumno_ve_dashboard(self):
        self.client.force_login(self.u_alumno)
        response = self.client.get(reverse('dashboard:inicio'))
        self.assertEqual(response.status_code, 200)

    def test_apoderado_ve_dashboard(self):
        self.client.force_login(self.u_apoderado)
        response = self.client.get(reverse('dashboard:inicio'))
        self.assertEqual(response.status_code, 200)

    def test_anonimo_redirige_a_login(self):
        response = self.client.get(reverse('dashboard:inicio'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response['Location'])

    def test_alumno_no_accede_chatbot(self):
        self.client.force_login(self.u_alumno)
        response = self.client.post(
            reverse('dashboard:chatbot_ia'),
            data='{"pregunta": "hola"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_apoderado_no_accede_chatbot(self):
        self.client.force_login(self.u_apoderado)
        response = self.client.post(
            reverse('dashboard:chatbot_ia'),
            data='{"pregunta": "hola"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
