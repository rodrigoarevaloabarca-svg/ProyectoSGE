# SGE — Sistema de Gestión Escolar

Sistema web desarrollado en Django para la gestión académica de colegios chilenos. Centraliza el manejo de alumnos, notas, asistencia, anotaciones, informes y comunicaciones entre todos los actores del establecimiento.

---

## Índice

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación local](#instalación-local)
- [Variables de entorno](#variables-de-entorno)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Roles y permisos](#roles-y-permisos)
- [Clonar Respositorio](#despliegue-en-Alwaysdata)
- [Comandos útiles](#comandos-útiles)

---

## Características

- **Multi-rol**: Administrador, Profesor, Alumno y Apoderado con vistas y permisos diferenciados
- **Libro de notas** con escala chilena (1.0–7.0) y cálculo automático de promedios vía signals
- **Registro de asistencia** diaria por asignatura con estados: Presente, Ausente, Atrasado, Justificado
- **Anotaciones** positivas y negativas por alumno
- **Informes académicos en PDF**: individual por período, ranking por curso, informe de fin de año e impresión masiva
- **Notificaciones internas** con envío masivo a apoderados y profesores
- **Historial de cambios** auditado para notas y anotaciones
- **Soporte dark/light mode** persistente por usuario
- **Diseño responsive** con Tailwind CSS y menú hamburguesa en móvil

---

## Requisitos

- Python 3.10+
- MySQL 8.0+ (o MariaDB 10.6+)
- pip

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE.git
cd ProyectoSGE
```

### 2. Crear entorno virtual

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con los valores correctos (ver sección [Variables de entorno](#variables-de-entorno)).

### 5. Crear la base de datos

```sql
-- En MySQL / MariaDB:
CREATE DATABASE sge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Aplicar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario administrador

```bash
python manage.py createsuperuser
```

### 8. Recolectar archivos estáticos

```bash
python manage.py collectstatic
```

### 9. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Abrir en el navegador: http://127.0.0.1:8000

---

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto. Usar `.env.example` como plantilla:

```env
# ── Seguridad ─────────────────────────────────────────────
SECRET_KEY=genera-una-clave-secreta-larga-y-aleatoria
DEBUG=True

# ── Hosts permitidos (separados por coma) ─────────────────
ALLOWED_HOSTS=localhost,127.0.0.1

# ── Base de datos ──────────────────────────────────────────
DB_NAME=sge_db
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_HOST=127.0.0.1
DB_PORT=3306

# ── Email (opcional en desarrollo) ────────────────────────
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=SGE Colegio <noreply@colegio.cl>

# ── CSRF (producción) ──────────────────────────────────────
CSRF_TRUSTED_ORIGINS=https://tu-dominio.pythonanywhere.com
```

> **Nunca subas el archivo `.env` al repositorio.** Ya está incluido en `.gitignore`.

Para generar una `SECRET_KEY` segura:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Estructura del proyecto

```
ProyectoSGE/
├── SGE/                    # Configuración principal del proyecto
│   ├── settings.py         # Configuración con variables de entorno
│   ├── urls.py             # URLs raíz
│   └── views.py            # Vistas de páginas públicas y errores
│
├── usuarios/               # Modelo de usuario personalizado y autenticación
├── alumnos/                # Perfiles y gestión de alumnos
├── profesores/             # Perfiles de profesores
├── apoderados/             # Perfiles de apoderados y relación con pupilos
├── cursos/                 # Cursos y niveles educacionales
├── asignaturas/            # Asignaturas por curso y profesor
├── notas/                  # Notas, tipos de evaluación y promedios (caché)
├── asistencia/             # Registros de asistencia diaria
├── anotaciones/            # Anotaciones conductuales (positivas/negativas)
├── informes/               # Períodos académicos e informes PDF
├── notificaciones/         # Sistema de mensajería interna y envíos masivos
├── historial/              # Auditoría de cambios en notas y anotaciones
├── dashboard/              # Vistas de inicio diferenciadas por rol
│
├── templates/              # Templates HTML compartidos (base.html, loginbase.html)
├── static/                 # CSS, JS estáticos del proyecto
│   ├── css/
│   │   ├── estilos.css
│   │   ├── navbar.css      # Estilos del navbar y dark mode
│   │   └── forms-dark.css  # Inputs visibles en modo oscuro
│   └── js/
│       ├── config.js
│       └── navbar.js       # Hamburguesa, dark mode persistente, mensajes flash
│
├── media/                  # Archivos subidos (fotos de perfil, logo) — NO versionado
├── requirements.txt        # Dependencias Python
├── manage.py
├── .env                    # Variables de entorno — NO versionado
└── .env.example            # Plantilla de variables de entorno
```

---

## Roles y permisos

| Acción | Admin | Profesor | Alumno | Apoderado |
|--------|:-----:|:--------:|:------:|:---------:|
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ |
| Ver alumnos | ✅ | ✅ | Solo propio | Solo pupilos |
| Crear / editar alumnos | ✅ | ❌ | ❌ | ❌ |
| Gestionar cursos y asignaturas | ✅ | ❌ | ❌ | ❌ |
| Ingresar y editar notas | ✅ | ✅ sus asignaturas | ❌ | ❌ |
| Tomar asistencia | ✅ | ✅ sus asignaturas | ❌ | ❌ |
| Crear anotaciones | ✅ | ✅ | ❌ | ❌ |
| Ver informes individuales | ✅ | ✅ | Solo propio | Solo pupilos |
| Centro de informes y PDF masivo | ✅ | ❌ | ❌ | ❌ |
| Enviar notificaciones masivas | ✅ | ❌ | ❌ | ❌ |
| Ver historial de cambios | ✅ | ❌ | ❌ | ❌ |

---

## clonar repositorio

En la consola Bash :

```bash
git clone https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE.git
cd ProyectoSGE
pip install -r requirements.txt --user
```

## Comandos útiles

```bash
# Crear y aplicar migraciones tras cambiar modelos
python manage.py makemigrations
python manage.py migrate

# Shell interactivo con contexto Django (útil para depurar)
python manage.py shell

# Ejecutar tests
python manage.py test

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Ver todas las URLs registradas
python manage.py show_urls  # requiere django-extensions
```

---

## Contacto

**Rodrigo Arévalo Abarca**  
📧 Rodrigoarevaloabarca@gmail.com  
📍 Rancagua, Chile

---

© 2026 Sistema de Gestión Escolar (SGE). Todos los derechos reservados.
