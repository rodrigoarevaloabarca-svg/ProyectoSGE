<div align="center">

# 🏫 SGE — Sistema de Gestión Escolar

**Sistema web completo para la gestión académica de colegios chilenos**

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge)](LICENSE)

Centraliza el manejo de **alumnos, notas, asistencia, anotaciones, informes PDF y comunicaciones** entre todos los actores del establecimiento — desde un solo sistema responsive con modo oscuro.

[📋 Características](#-características) · [🚀 Instalación](#-instalación-rápida) · [👥 Roles](#-roles-y-permisos) · [🌐 Deploy](#-despliegue-en-alwaysdata)

</div>

---

## 📋 Características

| Módulo | Descripción |
|--------|-------------|
| 👤 **Multi-rol** | Administrador, Profesor, Alumno y Apoderado con dashboards diferenciados |
| 📝 **Libro de notas** | Escala chilena 1.0–7.0, promedios automáticos vía Django signals |
| 📅 **Asistencia** | Registro diario por asignatura: Presente, Ausente, Atrasado, Justificado |
| 💬 **Anotaciones** | Positivas y negativas por alumno con historial auditado |
| 📄 **Informes PDF** | Individual, ranking por curso, fin de año e impresión masiva |
| 🔔 **Notificaciones** | Mensajería interna y envíos masivos a apoderados y profesores |
| 🕐 **Historial** | Auditoría completa de cambios en notas y anotaciones |
| 🌙 **Dark / Light mode** | Persistente por navegador, sin flash de tema al cargar |
| 📱 **Responsive** | Menú hamburguesa en móvil, diseño adaptable a cualquier pantalla |
| 🔒 **Seguridad** | Control de acceso granular por rol, CSRF, HSTS en producción |

---

## 🛠️ Stack tecnológico

```
Backend   →  Django 6.0 + MySQL 8
Frontend  →  Tailwind CSS + Material Symbols
PDF       →  ReportLab + pypdf
Auth      →  Django Auth con modelo de usuario personalizado y roles
Deploy    →  Alwaysdata + Gunicorn
```

---

## 🚀 Instalación rápida

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
# → Editar .env con tus credenciales

# 5. Base de datos (MySQL)
# CREATE DATABASE sge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

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

## ⚙️ Variables de entorno

Copiar `.env.example` a `.env` y completar los valores:

```env
SECRET_KEY=genera-una-clave-secreta-aleatoria
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=sge_db
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=127.0.0.1
DB_PORT=3306

# Email (en desarrollo imprime en consola, no envía correos reales)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

> 🔑 Generar `SECRET_KEY`:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## 🗂️ Estructura del proyecto

```
ProyectoSGE/
├── SGE/                    # Configuración principal (settings, urls, wsgi)
├── usuarios/               # Modelo de usuario personalizado + autenticación
├── alumnos/                # Perfiles y gestión de alumnos
├── profesores/             # Perfiles de profesores
├── apoderados/             # Apoderados y relación con pupilos
├── cursos/                 # Cursos y niveles educacionales
├── asignaturas/            # Asignaturas por curso y profesor
├── notas/                  # Notas, tipos de evaluación, caché de promedios
├── asistencia/             # Registros de asistencia diaria
├── anotaciones/            # Anotaciones conductuales
├── informes/               # Períodos académicos e informes PDF
├── notificaciones/         # Mensajería interna y envíos masivos
├── historial/              # Auditoría de cambios
├── dashboard/              # Vistas de inicio diferenciadas por rol
├── templates/              # HTML compartidos (base.html, loginbase.html)
├── static/                 # CSS y JS del proyecto
│   ├── css/
│   │   ├── navbar.css      # Hamburguesa + animación dark mode
│   │   ├── estilos.css     # configuracion general
│   │   ├── login-navbar.css# Nav bar login
│   │   └── forms-dark.css  # Inputs visibles en modo oscuro
│   │ 
│   └── js/
│       ├── Config.js       # configuracion general
│       ├── Login-forms.js  # Forms darkmode
│       └── navbar.js       # Dark mode persistente + menú hamburguesa
├── requirements.txt
├── .env.example
└── manage.py
```

---

## 👥 Roles y permisos

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

## 🌐 Despliegue en Alwaysdata

### 1. Subir código

En la consola SSH de Alwaysdata:

```bash
git clone https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE.git
cd ProyectoSGE
pip install -r requirements.txt --user
```

### 2. Configurar el sitio

En el panel **Web → Sites**, tipo **WSGI**, apuntar a:

```
/home/TU_CUENTA/ProyectoSGE/SGE/wsgi.py
```

### 3. Variables de entorno en producción

```bash
nano /home/TU_CUENTA/ProyectoSGE/.env
```

```env
DEBUG=False
ALLOWED_HOSTS=TU_CUENTA.alwaysdata.net
SECRET_KEY=clave-secreta-real
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
CSRF_TRUSTED_ORIGINS=https://TU_CUENTA.alwaysdata.net
```

### 4. Archivos estáticos

```bash
python manage.py collectstatic --noinput
```

En el panel **Web → Static files**:

| URL | Directorio |
|-----|------------|
| `/static/` | `/home/TU_CUENTA/ProyectoSGE/staticfiles/` |
| `/media/`  | `/home/TU_CUENTA/ProyectoSGE/media/` |

### 5. Base de datos y superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🧰 Comandos útiles

```bash
# Migraciones
python manage.py makemigrations && python manage.py migrate

# Shell interactivo con contexto Django
python manage.py shell

# Ejecutar tests
python manage.py test

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

---

## 📬 Contacto

**Rodrigo Arévalo Abarca**
📧 [Rodrigoarevaloabarca@gmail.com](mailto:Rodrigoarevaloabarca@gmail.com)
📍 Rancagua, Chile

---

<div align="center">

© 2026 Sistema de Gestión Escolar (SGE) · Todos los derechos reservados

</div>
