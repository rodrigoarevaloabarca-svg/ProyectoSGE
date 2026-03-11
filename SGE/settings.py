"""
Django settings para Sistema de Gestión Escolar (SGE)

Entornos soportados:
  - Desarrollo local  : DEBUG=True, MySQL Docker
  - Producción        : DEBUG=False, MySQL PythonAnywhere

Configuración sensible via variables de entorno (.env)
NUNCA hardcodear credenciales en este archivo.
"""
from pathlib import Path
import os

# ── Carga de variables de entorno (.env) ──────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # En PythonAnywhere las variables se definen en el panel web


def env(key, default=None, required=False):
    value = os.environ.get(key, default)
    if required and value is None:
        raise ValueError(f'Variable de entorno requerida no definida: {key}')
    return value


def env_bool(key, default=False):
    return env(key, str(default)).lower() in ('true', '1', 'yes')


def env_list(key, default=''):
    value = env(key, default)
    return [v.strip() for v in value.split(',') if v.strip()]


# ── Rutas base ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent


# ── Seguridad principal ───────────────────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY', required=True)
DEBUG       = env_bool('DEBUG', default=False)
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', default='localhost,127.0.0.1')


# ── Aplicaciones instaladas ───────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'alumnos',
    'profesores',
    'apoderados',
    'cursos',
    'asignaturas',
    'notas',
    'asistencia',
    'anotaciones',
    'dashboard',
    'informes',
    'notificaciones',
]


# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SGE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notificaciones.context_processors.notificaciones_no_leidas',
            ],
        },
    },
]

WSGI_APPLICATION = 'SGE.wsgi.application'


# ── Base de datos ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     env('DB_NAME', 'sge_db'),
        'USER':     env('DB_USER', 'root'),
        'PASSWORD': env('DB_PASSWORD', required=True),
        'HOST':     env('DB_HOST', '127.0.0.1'),
        'PORT':     env('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 60,
    }
}


# ── Validación de contraseñas ─────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'usuarios.Usuario'


# ── Internacionalización ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-cl'
TIME_ZONE     = 'America/Santiago'
USE_I18N      = True
USE_TZ        = True


# ── Archivos estáticos y media ────────────────────────────────────────────────
STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL        = '/media/'
MEDIA_ROOT       = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── Autenticación y sesiones ──────────────────────────────────────────────────
LOGIN_URL           = '/usuarios/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/usuarios/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE      = 60 * 60 * 8   # 8 horas (jornada escolar)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'


# ── Mensajes ──────────────────────────────────────────────────────────────────
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG:   'debug',
    messages.INFO:    'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR:   'danger',
}


# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = env('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST          = env('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(env('EMAIL_PORT', '587'))
EMAIL_USE_TLS       = env_bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER     = env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = env('DEFAULT_FROM_EMAIL', 'SGE Colegio <noreply@colegio.cl>')


# ── Seguridad HTTP (todos los entornos) ───────────────────────────────────────
SECURE_BROWSER_XSS_FILTER   = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS              = 'DENY'
CSRF_COOKIE_HTTPONLY         = False   # JS necesita leer el token CSRF
CSRF_COOKIE_SAMESITE         = 'Lax'
CSRF_TRUSTED_ORIGINS         = env_list(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost,http://127.0.0.1'
)


# ── Solo en PRODUCCIÓN ────────────────────────────────────────────────────────
if not DEBUG:
    # Forzar HTTPS
    SECURE_SSL_REDIRECT            = True
    SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS: solo HTTPS por 1 año
    SECURE_HSTS_SECONDS            = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD            = True

    # Cookies seguras solo por HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE    = True

    # Carpeta de logs (crear manualmente: mkdir logs)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'logs' / 'errores.log',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }
