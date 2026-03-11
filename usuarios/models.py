"""
APP: usuarios
ARCHIVO: models.py

Modelo de usuario personalizado con sistema de roles.
Extiende AbstractUser para mantener toda la funcionalidad
de autenticación de Django más los roles del colegio.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuario personalizado del sistema.
    Extiende AbstractUser (ya tiene: username, password, email,
    first_name, last_name, is_active, is_staff, date_joined)
    """

    # Roles disponibles en el sistema
    ROL_ADMIN = 'admin'
    ROL_PROFESOR = 'profesor'
    ROL_APODERADO = 'apoderado'
    ROL_ALUMNO = 'alumno'

    ROLES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_PROFESOR, 'Profesor'),
        (ROL_APODERADO, 'Apoderado'),
        (ROL_ALUMNO, 'Alumno'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default=ROL_ALUMNO,
        verbose_name='Rol en el sistema'
    )

    rut = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        verbose_name='RUT',
        help_text='Formato: 12345678-9'
    )

    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )

    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        null=True,
        blank=True,
        verbose_name='Foto de perfil'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    # ---- Métodos helper para verificar rol en templates ----
    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN

    @property
    def es_profesor(self):
        return self.rol == self.ROL_PROFESOR

    @property
    def es_apoderado(self):
        return self.rol == self.ROL_APODERADO

    @property
    def es_alumno(self):
        return self.rol == self.ROL_ALUMNO
