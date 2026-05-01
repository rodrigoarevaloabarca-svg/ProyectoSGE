from .base import *  # noqa: F401, F403
from .base import BASE_DIR

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# SQLite3 local — evita depender de MySQL en desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Deshabilitar bloqueo de intentos en dev (facilita pruebas)
AXES_ENABLED = False
