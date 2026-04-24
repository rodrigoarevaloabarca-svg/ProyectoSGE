from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Deshabilitar axes en tests para no bloquear usuarios de prueba
AXES_ENABLED = False
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# Contraseñas más rápidas en tests
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
