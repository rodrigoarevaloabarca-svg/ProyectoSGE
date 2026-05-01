# Guía de Contribución — SGE

Gracias por contribuir al Sistema de Gestión Escolar. Esta guía cubre todo lo necesario para configurar el entorno, seguir las convenciones del proyecto y enviar cambios de calidad.

---

## Tabla de contenidos

1. [Requisitos previos](#1-requisitos-previos)
2. [Configuración del entorno](#2-configuración-del-entorno)
3. [Variables de entorno](#3-variables-de-entorno)
4. [Estructura de settings](#4-estructura-de-settings)
5. [Flujo de trabajo Git](#5-flujo-de-trabajo-git)
6. [Tests](#6-tests)
7. [Linter y formato](#7-linter-y-formato)
8. [Pre-commit hooks](#8-pre-commit-hooks)
9. [Migraciones](#9-migraciones)
10. [Convenciones de código](#10-convenciones-de-código)
11. [Roles y seguridad](#11-roles-y-seguridad)
12. [Reportar vulnerabilidades](#12-reportar-vulnerabilidades)

---

## 1. Requisitos previos

| Herramienta | Versión mínima |
|---|---|
| Python | 3.10 |
| MySQL | 8.0 (o MariaDB 10.6) |
| Git | 2.x |

---

## 2. Configuración del entorno

```bash
# Clonar el repositorio
git clone https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE.git
cd ProyectoSGE

# Crear entorno virtual
python -m venv .venv
source .venv/Scripts/activate   # Windows
# source .venv/bin/activate     # Linux / macOS

# Instalar dependencias de producción y desarrollo
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar variables de entorno
cp .env.example .env
# → Editar .env con las credenciales locales

# Crear base de datos MySQL
mysql -u root -p -e "CREATE DATABASE sge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Aplicar migraciones y crear superusuario
python manage.py migrate
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```

Abrir → [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 3. Variables de entorno

Archivo `.env` (basado en `.env.example`):

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Módulo de settings activo | `SGE.settings.development` |
| `SECRET_KEY` | Clave secreta Django (mínimo 50 caracteres) | *(generada con `get_random_secret_key()`)* |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos (coma separados) | `localhost,127.0.0.1` |
| `DB_NAME` | Nombre de la base de datos | `sge_db` |
| `DB_USER` | Usuario MySQL | `root` |
| `DB_PASSWORD` | Contraseña MySQL | `tu_contraseña` |
| `DB_HOST` | Host MySQL | `127.0.0.1` |
| `DB_PORT` | Puerto MySQL | `3306` |
| `GROQ_API_KEY` | API key de Groq para funciones IA | `gsk_...` |
| `EMAIL_HOST_USER` | Correo Gmail para envío (solo producción) | `noreply@colegio.cl` |
| `EMAIL_HOST_PASSWORD` | App password Gmail (solo producción) | |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables (solo producción) | `https://example.com` |
| `OTP_TOTP_ISSUER` | Nombre en apps autenticadoras (opcional) | `SGE Colegio` |

Generar una `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 4. Estructura de settings

Los settings están divididos en `SGE/settings/` por entorno:

| Módulo | Uso | Notas |
|---|---|---|
| `base.py` | Configuración compartida | MySQL, apps instaladas, middleware, seguridad base |
| `development.py` | Desarrollo local | `DEBUG=True`, `ALLOWED_HOSTS=['localhost']` |
| `production.py` | Producción | HTTPS, HSTS, cookies seguras, `ManifestStaticFilesStorage`, logs rotativos |
| `testing.py` | CI y pytest | SQLite en memoria, `AXES_ENABLED=False`, hasher rápido |

El settings activo se controla con la variable `DJANGO_SETTINGS_MODULE`.
- `manage.py` usa `development` por defecto
- `wsgi.py` usa `production` por defecto

---

## 5. Flujo de trabajo Git

```bash
# 1. Crear rama desde main
git checkout main && git pull
git checkout -b feat/nombre-feature
# Prefijos: feat/, fix/, refactor/, docs/, test/, chore/

# 2. Hacer commits descriptivos
git commit -m "feat(notas): agregar validación de nota mínima por asignatura"

# 3. Asegurar que tests y linter pasen
pytest
ruff check .

# 4. Push y Pull Request hacia main
git push origin feat/nombre-feature
```

### Convención de commits

```
<tipo>(<app>): <descripción corta en imperativo>

Tipos: feat | fix | refactor | docs | test | chore | security | perf
```

---

## 6. Tests

### Ejecutar tests

```bash
# Rápido (SQLite en memoria — usa settings/testing.py)
pytest

# Completo con MySQL (como en CI)
python manage.py test

# Con cobertura
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Solo un módulo
pytest alumnos/tests.py
pytest notas/tests.py -v
```

### Dónde escribir tests

| Archivo | Qué cubre |
|---|---|
| `usuarios/tests.py` | Propiedades del modelo Usuario, validación de RUT |
| `alumnos/tests.py` | IDOR: alumno solo ve su propio perfil |
| `notas/tests.py` | Señales: `PromedioAsignatura` se recalcula en save/delete |
| `asistencia/tests.py` | Método bulk `tomar_asistencia_curso()` |
| `informes/tests.py` | Generación de datos, descarga de PDF |
| `dashboard/tests.py` | Dashboard diferenciado por rol |

### Convenciones de tests

- Usar `TestCase` de Django (con transacciones por test)
- El DB de tests es SQLite en memoria (`settings/testing.py`) — no requiere MySQL instalado
- Crear fixtures con `setUp()` o factories simples; evitar fixtures de JSON
- No mockear la base de datos — los tests de integración deben leer/escribir datos reales
- Nombrar métodos: `test_<qué>_<condición>_<resultado_esperado>`

---

## 7. Linter y formato

Este proyecto usa **ruff** como linter y formatter unificado.

```bash
ruff check .              # Verificar errores y advertencias
ruff check . --fix        # Corregir automáticamente lo que sea posible
ruff format .             # Formatear código
ruff check . --select E   # Solo errores de estilo
```

Configuración en `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
```

El CI bloquea merges si `ruff check .` falla.

---

## 8. Pre-commit hooks

```bash
# Instalar hooks (una sola vez por clon)
pre-commit install

# Ejecutar manualmente en todos los archivos
pre-commit run --all-files
```

Hooks configurados en `.pre-commit-config.yaml`:
- `ruff` — linting y auto-fix
- `trailing-whitespace` — elimina espacios al final de línea
- `debug-statements` — bloquea `print()`, `pdb`, `breakpoint()` en commits

---

## 9. Migraciones

Después de modificar cualquier modelo:

```bash
python manage.py makemigrations <app>   # preferir indicar la app
python manage.py migrate
```

### Reglas para migraciones

- Nunca editar migraciones ya aplicadas en `main`
- Siempre incluir la migración generada en el mismo commit que el cambio de modelo
- Si hay datos existentes, añadir una migración de datos (`RunPython`) antes de restricciones nuevas
- Para renombrar campos, usar `RenameField` en lugar de borrar y recrear (preserva datos)

---

## 10. Convenciones de código

### Vistas

```python
# Toda vista nueva debe:
# 1. Tener @login_required mínimamente
# 2. Aplicar el decorador de rol apropiado
# 3. Usar select_related() para evitar N+1

@login_required
@solo_admin_o_profesor
def mi_vista(request, alumno_id):
    alumno = get_object_or_404(
        Alumno.objects.select_related('usuario', 'curso__nivel'),
        pk=alumno_id
    )
    ...
```

### Promedios

```python
# CORRECTO — usa caché
from notas.models import PromedioAsignatura
promedio = PromedioAsignatura.objects.get(alumno=alumno, asignatura=asig)

# INCORRECTO — recalcula en cada request
from django.db.models import Avg
promedio = Nota.objects.filter(...).aggregate(Avg('valor'))['valor__avg']
```

### Datos de informes

```python
# CORRECTO — usa el servicio centralizado
from informes.services import InformeService
datos = InformeService.recopilar_datos(alumno, periodo)

# INCORRECTO — recopilar datos directamente en la vista
notas = Nota.objects.filter(alumno=alumno, ...)
```

### Auditoría académica

Cuando una vista modifica una nota o anotación, registrar el cambio:

```python
from historial.utils import snapshot_nota, registrar_cambio_nota

antes = snapshot_nota(nota)
nota.save()
despues = snapshot_nota(nota)
registrar_cambio_nota(antes, despues, request.user)
```

### Auditoría de eventos de usuario

Para eventos de seguridad sobre un usuario (cambio de rol, desactivación, etc.):

```python
from historial.models import HistorialCambio
from historial.utils import registrar_evento_usuario

registrar_evento_usuario(
    usuario_pk=usuario.pk,
    accion=HistorialCambio.ACCION_CAMBIO_ROL,   # o ACCION_DESACTIVACION, etc.
    datos={'campo': 'valor_anterior'},
    modificado_por=request.user,
    descripcion=str(usuario),
)
```

Los eventos de login/logout/login_fallido se registran **automáticamente** mediante señales Django en `usuarios/signals.py`. No es necesario llamarlos desde las vistas.

### Logging de seguridad

Usar el logger `sge.seguridad` para eventos de seguridad en vistas:

```python
import logging
logger = logging.getLogger('sge.seguridad')

logger.warning('ACCIÓN_CRÍTICA | usuario=%s | ip=%s', username, ip)
```

En desarrollo, los mensajes van a la consola. En producción, se escriben en `logs/seguridad.log`.

---

## 11. Roles y seguridad

### Tabla de permisos

| Acción | Admin | Profesor | Alumno | Apoderado |
|--------|:-----:|:--------:|:------:|:---------:|
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ |
| Ver cualquier alumno | ✅ | ✅ | ❌ | ❌ |
| Ver propio perfil | ✅ | ✅ | ✅ | ❌ |
| Ver pupilos (apoderado) | ✅ | ✅ | ❌ | ✅ |
| Crear / editar alumnos | ✅ | ❌ | ❌ | ❌ |
| Gestionar cursos y asignaturas | ✅ | ❌ | ❌ | ❌ |
| Ingresar y editar notas | ✅ | ✅ sus asignaturas | ❌ | ❌ |
| Tomar asistencia | ✅ | ✅ sus asignaturas | ❌ | ❌ |
| Crear / editar anotaciones | ✅ | ✅ | ❌ | ❌ |
| Ver informe propio / pupilo | ✅ | ✅ | ✅ propio | ✅ pupilo |
| Centro de informes y PDF masivo | ✅ | ❌ | ❌ | ❌ |
| Chatbot IA | ✅ | ✅ | ❌ | ❌ |
| Enviar notificaciones masivas | ✅ | ❌ | ❌ | ❌ |
| Ver historial de cambios | ✅ | ❌ | ❌ | ❌ |

### Decoradores disponibles

```python
from usuarios.decorators import solo_admin, solo_admin_o_profesor, puede_ver_alumno

@solo_admin                     # Solo rol == 'admin'
@solo_admin_o_profesor          # Admin o Profesor
@puede_ver_alumno('pk')         # IDOR-safe: valida propiedad por rol
```

### IDOR

El decorador `@puede_ver_alumno` valida que el usuario tiene derecho a ver al alumno especificado en la URL. Aplicar **siempre** en vistas que reciben un `alumno_id` o `pk` en la URL y devuelven datos del alumno.

### Perfil de usuario

Todos los roles pueden editar sus propios datos básicos (nombre, email, RUT, teléfono, foto) usando `UsuarioPerfilForm`. Solo los admins pueden cambiar el `rol` o `is_active` de otros usuarios (via `UsuarioEdicionForm` en la vista `editar_usuario`).

### 2FA

El 2FA es opcional pero recomendado para administradores. El enrollment se hace desde la página de perfil. En desarrollo no es necesario configurarlo. El panel `/admin/` solo exige OTP si el usuario tiene un dispositivo TOTP confirmado.

---

## 12. Reportar vulnerabilidades

Ver [SECURITY.md](SECURITY.md) para la política de divulgación y el checklist de producción.

No abrir issues públicos para reportar vulnerabilidades de seguridad. Contactar directamente a:
**rodrigoarevaloabarca@gmail.com**
