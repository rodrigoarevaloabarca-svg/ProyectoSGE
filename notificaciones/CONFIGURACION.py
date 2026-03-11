"""
CONFIGURACIÓN DE EMAIL Y NOTIFICACIONES
=======================================
Agrega esto a D:\Gestion\colegio_chile\settings.py

PASO 1 — Registrar la app y el context processor
"""

# En INSTALLED_APPS agrega:
INSTALLED_APPS = [
    # ... apps existentes ...
    'notificaciones',   # ← agregar
]

# En TEMPLATES > OPTIONS > context_processors agrega:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['BASE_DIR / templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notificaciones.context_processors.notificaciones_no_leidas',  # ← agregar
            ],
        },
    },
]


"""
PASO 2 — Configuración de Email

OPCIÓN A: Gmail (más fácil para empezar)
-----------------------------------------
1. Ve a tu cuenta Gmail → Seguridad → Verificación en 2 pasos → Contraseñas de aplicación
2. Genera una contraseña para "Correo" / "Windows"
3. Usa esa contraseña de 16 caracteres en EMAIL_HOST_PASSWORD
"""

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'tu_correo@gmail.com'       # ← tu correo Gmail
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'        # ← contraseña de aplicación (16 chars)
DEFAULT_FROM_EMAIL  = 'SGE Colegio <tu_correo@gmail.com>'

"""
OPCIÓN B: Solo para desarrollo — muestra emails en consola (sin enviar nada)
Útil para probar sin configurar Gmail todavía.
"""
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

"""
OPCIÓN C: Guardar emails como archivos en carpeta local
"""
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = BASE_DIR / 'emails_debug'

"""
PASO 3 — Agregar URL en SGE/urls.py

Dentro de urlpatterns agrega:
    path('notificaciones/', include('notificaciones.urls', namespace='notificaciones')),

PASO 4 — Migrar la base de datos
    python manage.py makemigrations notificaciones
    python manage.py migrate

PASO 5 — Proteger credenciales en .env
Mueve las credenciales sensibles al .env:

    # .env
    EMAIL_HOST_USER=tu_correo@gmail.com
    EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx

Y en settings.py léelas con:
    import os
    EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL  = f'SGE Colegio <{EMAIL_HOST_USER}>'
"""
