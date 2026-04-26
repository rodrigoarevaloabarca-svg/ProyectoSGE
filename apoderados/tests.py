from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apoderados.models import Apoderado

Usuario = get_user_model()


class ApoderadoAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Usuario.objects.create_user(
            username='admin_test', password='admin12345678', rol='admin'
        )
        self.u_alumno = Usuario.objects.create_user(
            username='alumno_test', password='alumno12345678', rol='alumno'
        )
        self.u_apoderado = Usuario.objects.create_user(
            username='apoderado_test', password='apod12345678', rol='apoderado'
        )
        self.apoderado = Apoderado.objects.create(usuario=self.u_apoderado)

    def test_alumno_no_puede_listar_apoderados(self):
        self.client.force_login(self.u_alumno)
        response = self.client.get(reverse('apoderados:lista'))
        self.assertRedirects(response, reverse('dashboard:inicio'))

    def test_apoderado_no_puede_listar_apoderados(self):
        self.client.force_login(self.u_apoderado)
        response = self.client.get(reverse('apoderados:lista'))
        self.assertRedirects(response, reverse('dashboard:inicio'))

    def test_alumno_no_puede_crear_apoderado(self):
        self.client.force_login(self.u_alumno)
        response = self.client.get(reverse('apoderados:crear'))
        self.assertRedirects(response, reverse('dashboard:inicio'))

    def test_alumno_no_puede_editar_apoderado(self):
        self.client.force_login(self.u_alumno)
        response = self.client.get(reverse('apoderados:editar', kwargs={'pk': self.apoderado.pk}))
        self.assertRedirects(response, reverse('dashboard:inicio'))

    def test_admin_puede_listar_apoderados(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('apoderados:lista'))
        self.assertEqual(response.status_code, 200)

    def test_apoderado_puede_ver_su_propio_detalle(self):
        self.client.force_login(self.u_apoderado)
        response = self.client.get(reverse('apoderados:detalle', kwargs={'pk': self.apoderado.pk}))
        self.assertEqual(response.status_code, 200)

    def test_apoderado_no_puede_ver_detalle_ajeno(self):
        otro_u = Usuario.objects.create_user(
            username='otro_apod', password='otro12345678', rol='apoderado'
        )
        otro = Apoderado.objects.create(usuario=otro_u)
        self.client.force_login(self.u_apoderado)
        response = self.client.get(reverse('apoderados:detalle', kwargs={'pk': otro.pk}))
        self.assertRedirects(response, reverse('dashboard:inicio'))
