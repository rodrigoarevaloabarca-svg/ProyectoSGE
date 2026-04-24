<div align="center">

# SGE — Sistema de Gestión Escolar

**Sistema web completo para la gestión académica de colegios chilenos**

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![CI](https://img.shields.io/github/actions/workflow/status/rodrigoarevaloabarca-svg/ProyectoSGE/ci.yml?branch=main&style=for-the-badge&label=CI)](https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE/actions)
[![License](https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge)](LICENSE)

Centraliza el manejo de **alumnos, notas, asistencia, anotaciones, informes PDF y comunicaciones** entre todos los actores del establecimiento — desde un solo sistema responsive con modo oscuro.

[Características](#-características) · [Instalación](#-instalación-rápida) · [Roles y permisos](#-roles-y-permisos) · [Deploy](#-despliegue-en-producción)

</div>

---

## Características

| Módulo | Descripción |
|--------|-------------|
| **Multi-rol** | Administrador, Profesor, Alumno y Apoderado con dashboards diferenciados y control de acceso granular |
| **Libro de notas** | Escala chilena 1.0–7.0, promedios automáticos actualizados por Django signals en tiempo real |
| **Asistencia** | Registro diario por asignatura: Presente, Ausente, Atrasado, Justificado. Toma de asistencia para curso completo en una sola operación |
| **Anotaciones** | Positivas y negativas por alumno, categorizadas, con firma de apoderado y historial auditado |
| **Informes PDF** | Individual por alumno/período, ranking por curso, informe de fin de año, impresión masiva (pypdf) |
| **Notificaciones** | Mensajería interna 1:1 y envíos masivos a apoderados, profesores o cursos específicos |
| **Auditoría** | Historial completo de cambios en notas y anotaciones con snapshots JSON antes/después |
| **IA académica** | Análisis de riesgo por alumno y chatbot pedagógico mediante Groq (llama-3.1-8b-instant) |
| **Dark / Light mode** | Persistente por navegador, sin flash de tema al cargar |
| **Responsive** | Menú hamburguesa en móvil, diseño adaptable a cualquier pantalla |
| **Seguridad** | IDOR prevention, django-axes, CSRF, HSTS, cookies seguras, validación de imágenes con PIL |

---

## Stack tecnológico

```
Backend     →  Django 6.0 + MySQL 8.0
Frontend    →  Tailwind CSS 3.x + Material Symbols
PDF         →  ReportLab + pypdf
IA          →  Groq API (llama-3.1-8b-instant)
Auth        →  Django Auth + AbstractUser + django-axes
CI/CD       →  GitHub Actions (lint + test en MySQL)
Deploy      →  Gunicorn + Alwaysdata (WSGI)
```

---

## Instalación rápida

### Prerrequisitos

- Python 3.10+
- MySQL 8.0+ (o MariaDB 10.6+)

### Pasos

```bash
# 1. Clonar
git clone https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE.git
cd ProyectoSGE

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# → Editar .env con tus credenciales (ver sección siguiente)

# 5. Base de datos (MySQL)
mysql -u root -p -e "CREATE DATABASE sge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 6. Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# 7. Archivos estáticos
python manage.py collectstatic

# 8. Servidor de desarrollo
python manage.py runserver
```

Abrir → http://127.0.0.1:8000

---

## Variables de entorno

Copiar `.env.example` a `.env` y completar los valores:

```env
# Django
DJANGO_SETTINGS_MODULE=SGE.settings.development
SECRET_KEY=genera-una-clave-secreta-aleatoria
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=sge_db
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=127.0.0.1
DB_PORT=3306

# IA (opcional para funciones de análisis y chatbot)
GROQ_API_KEY=gsk_...

# Email (en desarrollo imprime en consola, no envía correos reales)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Generar `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Estructura del proyecto

```
ProyectoSGE/
├── SGE/                        # Configuración principal Django
│   ├── settings/
│   │   ├── base.py             # Config compartida (MySQL, apps, seguridad)
│   │   ├── development.py      # DEBUG=True, hosts locales
│   │   ├── production.py       # HTTPS, HSTS, logs rotativos
│   │   └── testing.py          # SQLite en memoria, tests rápidos
│   ├── urls.py                 # Routing principal (14 apps)
│   ├── ia_utils.py             # Integración Groq (análisis riesgo, chatbot)
│   └── wsgi.py                 # Entrada WSGI de producción
│
├── usuarios/                   # Autenticación y gestión de usuarios
│   ├── models.py               # Usuario(AbstractUser) con campo rol
│   ├── decorators.py           # @solo_admin, @puede_ver_alumno, etc.
│   └── validators.py           # validar_rut, validar_nota (reutilizables)
│
├── alumnos/                    # Perfiles de alumnos
├── profesores/                 # Perfiles de profesores
├── apoderados/                 # Apoderados y relación con pupilos
├── cursos/                     # Cursos y niveles educacionales
├── asignaturas/                # Asignaturas por curso y profesor
│
├── notas/                      # Notas y promedios
│   ├── models.py               # Nota (1.0–7.0), PromedioAsignatura (caché)
│   └── signals.py              # Recalcula PromedioAsignatura en post_save/delete
│
├── asistencia/                 # Registros de asistencia diaria
│   └── models.py               # RegistroAsistencia + tomar_asistencia_curso()
│
├── anotaciones/                # Anotaciones conductuales
├── informes/                   # Períodos académicos e informes PDF
│   ├── services.py             # InformeService.recopilar_datos()
│   ├── pdf_generator.py        # PDF individual (ReportLab)
│   └── pdf_reportes.py         # PDF ranking y fin de año
│
├── notificaciones/             # Mensajería interna y envíos masivos
├── historial/                  # Auditoría de cambios (JSON snapshots)
├── dashboard/                  # Dashboards diferenciados por rol + chatbot IA
│
├── templates/                  # Plantillas HTML compartidas
│   ├── base.html               # Layout principal (navbar, footer, dark mode)
│   └── loginbase.html          # Layout de autenticación
│
├── static/                     # Assets frontend
│   ├── css/                    # TailwindCSS compilado, estilos dark mode
│   └── js/                     # navbar.js (dark mode), chatbot widget
│
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # pytest, ruff, coverage, pre-commit
├── pyproject.toml              # Configuración de ruff y pytest
├── .env.example                # Plantilla de variables de entorno
└── manage.py
```

---

## Roles y permisos

| Acción | Admin | Profesor | Alumno | Apoderado |
|--------|:-----:|:--------:|:------:|:---------:|
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ |
| Ver cualquier alumno | ✅ | ✅ | ❌ | ❌ |
| Ver propio perfil | ✅ | ✅ | ✅ | ❌ |
| Ver sus pupilos | ✅ | ✅ | ❌ | ✅ |
| Crear / editar alumnos | ✅ | ❌ | ❌ | ❌ |
| Gestionar cursos y asignaturas | ✅ | ❌ | ❌ | ❌ |
| Ingresar y editar notas | ✅ | ✅ sus asignaturas | ❌ | ❌ |
| Tomar asistencia | ✅ | ✅ sus asignaturas | ❌ | ❌ |
| Crear / editar anotaciones | ✅ | ✅ | ❌ | ❌ |
| Ver informe individual | ✅ | ✅ sus alumnos | ✅ propio | ✅ sus pupilos |
| Centro de informes y PDF masivo | ✅ | ❌ | ❌ | ❌ |
| Chatbot IA | ✅ | ✅ | ❌ | ❌ |
| Enviar notificaciones masivas | ✅ | ❌ | ❌ | ❌ |
| Ver historial de cambios | ✅ | ❌ | ❌ | ❌ |

---

## Funciones de IA

### Análisis de riesgo académico

Disponible en la vista de detalle de cada alumno (solo admin y profesores). El sistema recopila:

- Promedio general y por asignatura
- Porcentaje de asistencia
- Cantidad de anotaciones negativas recientes

Con estos datos anonimizados, Groq genera un análisis de riesgo (alto/medio/bajo) con recomendaciones pedagógicas. El resultado se cachea durante 1 hora.

### Chatbot pedagógico

Disponible en el dashboard de admin y profesores. Permite consultar información académica sobre alumnos o cursos en lenguaje natural. El chatbot:

- Filtra la información según el rol del usuario
- Anonimiza los datos antes de enviarlos a Groq
- Re-mapea los IDs a nombres reales en la respuesta
- Protege contra prompt injection con delimitadores explícitos

**Privacidad**: ningún nombre, RUT ni dato de contacto se envía a Groq.

---

## Desarrollo y tests

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests (SQLite en memoria — rápido)
pytest

# Tests con cobertura
pytest --cov=. --cov-report=html

# Linter
ruff check .
ruff check . --fix

# Pre-commit hooks
pre-commit install
```

El pipeline de CI ejecuta `ruff check .` y `pytest` (con MySQL) en cada push a `main`.

---

## Despliegue en producción

### Variables de entorno de producción

```env
DJANGO_SETTINGS_MODULE=SGE.settings.production
DEBUG=False
SECRET_KEY=<clave-larga-y-aleatoria>
ALLOWED_HOSTS=tu-dominio.cl
CSRF_TRUSTED_ORIGINS=https://tu-dominio.cl
DB_NAME=sge_db
DB_USER=sge_user
DB_PASSWORD=<contraseña-fuerte>
DB_HOST=127.0.0.1
DB_PORT=3306
GROQ_API_KEY=gsk_...
EMAIL_HOST_USER=noreply@tu-dominio.cl
EMAIL_HOST_PASSWORD=<app-password>
```

### Despliegue en Alwaysdata

```bash
# 1. Clonar en el servidor
git clone https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE.git
cd ProyectoSGE
pip install -r requirements.txt --user

# 2. Configurar .env de producción
nano .env

# 3. Migraciones y estáticos
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

En el panel **Web → Sites**, tipo **WSGI**, apuntar a:
```
/home/TU_CUENTA/ProyectoSGE/SGE/wsgi.py
```

En **Web → Static files**:

| URL | Directorio |
|-----|------------|
| `/static/` | `/home/TU_CUENTA/ProyectoSGE/staticfiles/` |
| `/media/` | `/home/TU_CUENTA/ProyectoSGE/media/` |

### Verificar despliegue seguro

```bash
python manage.py check --deploy
```

No debe haber errores críticos (WARNINGS de HSTS son esperados si no está configurado SSL en el servidor).

---

## Comandos útiles

```bash
# Desarrollo
python manage.py runserver
python manage.py shell
python manage.py createsuperuser

# Migraciones
python manage.py makemigrations <app>
python manage.py migrate

# Producción
python manage.py collectstatic --noinput
python manage.py check --deploy

# Tests
pytest
pytest --cov=. --cov-report=html
python manage.py test

# Calidad de código
ruff check .
ruff check . --fix
ruff format .
```

---

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para la guía completa de configuración, convenciones y flujo de trabajo.

---

## Seguridad

Ver [SECURITY.md](SECURITY.md) para la política de divulgación de vulnerabilidades y el checklist de seguridad en producción.

---

## Contacto

**Rodrigo Arévalo Abarca**
📧 [rodrigoarevaloabarca@gmail.com](mailto:rodrigoarevaloabarca@gmail.com)
📍 Rancagua, Chile

---

<div align="center">

© 2026 Sistema de Gestión Escolar (SGE) · Todos los derechos reservados

</div>
