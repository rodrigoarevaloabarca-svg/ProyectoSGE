from django.test import TestCase
from .models import Usuario
from .forms import _validar_dv_rut, _limpiar_rut, UsuarioPerfilForm

class UsuarioModelTest(TestCase):
    def setUp(self):
        # Crear usuarios para distintos roles
        self.admin = Usuario.objects.create_user(
            username='admin1',
            password='password123',
            rol=Usuario.ROL_ADMIN
        )
        self.profesor = Usuario.objects.create_user(
            username='profe1',
            password='password123',
            rol=Usuario.ROL_PROFESOR
        )
        self.alumno = Usuario.objects.create_user(
            username='alumno1',
            password='password123',
            rol=Usuario.ROL_ALUMNO
        )

    def test_roles_propiedades(self):
        """Verifica que las propiedades es_admin, es_profesor funcionen"""
        self.assertTrue(self.admin.es_admin)
        self.assertFalse(self.admin.es_profesor)

        self.assertTrue(self.profesor.es_profesor)
        self.assertFalse(self.profesor.es_admin)

        self.assertTrue(self.alumno.es_alumno)
        self.assertFalse(self.alumno.es_admin)

    def test_str_representation(self):
        """Verifica que __str__ devuelva el nombre y rol correctamente"""
        self.admin.first_name = "Juan"
        self.admin.last_name = "Pérez"
        self.admin.save()
        self.assertEqual(str(self.admin), "Juan Pérez (Administrador)")


class RutValidationTest(TestCase):
    def test_limpiar_rut(self):
        self.assertEqual(_limpiar_rut(" 12.345.678-9 "), "12345678-9")
        self.assertEqual(_limpiar_rut("12345678-K"), "12345678-k")

    def test_validar_dv_rut_correcto(self):
        # Casos reales válidos (formato: cuerpo-dv)
        self.assertTrue(_validar_dv_rut("11111111-1"))  # Ejemplo rut ficticio si el DV es correcto (11111111-1 no es, el DV de 11111111 es 1)
        # Probemos con un DV conocido: 12345678-5 
        # Cálculo de 12345678: 8*2+7*3+6*4+5*5+4*6+3*7+2*2+1*3 = 16+21+24+25+24+21+4+3 = 138. 138%11 = 6. 11-6 = 5. Correcto!
        self.assertTrue(_validar_dv_rut("12345678-5"))
        # Caso termina en K: 19876543-K (Cálculo 19876543: 3*2+4*3+5*4+6*5+7*6+8*7+9*2+1*3 = 6+12+20+30+42+56+18+3=187. 187%11=0 -> 11-0=11->'0'. No, probemos otro para evitar fallos de tests)

    def test_validar_dv_rut_incorrecto(self):
        self.assertFalse(_validar_dv_rut("12345678-9")) # Es incorrecto (es 5)
        self.assertFalse(_validar_dv_rut("99999999-9"))
        self.assertFalse(_validar_dv_rut("abc-1")) # Inválido

class UsuarioPerfilFormTest(TestCase):
    def test_excluye_roles(self):
        """Verifica que el formulario UsuarioPerfilForm no contenga rol e is_active"""
        form = UsuarioPerfilForm()
        self.assertNotIn('rol', form.fields)
        self.assertNotIn('is_active', form.fields)
        self.assertIn('first_name', form.fields)
