# Changelog — SGE

Todos los cambios notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).
Versionado según [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.1.0] — 2026-04-24

Esta versión consolida una ronda completa de seguridad, rendimiento, refactoring e infraestructura. No introduce cambios de ruptura en la base de datos — las migraciones existentes son compatibles.

### Seguridad

- **Anonimización de datos en Groq**: nombres, cursos y asignaturas reemplazados por IDs internos (`ESTUDIANTE_{id}`, `CURSO_{id}`, `ASIG_{id}`) antes de enviar cualquier dato a la API externa
- **Prevención de prompt injection**: entrada del usuario encapsulada con delimitadores `<user_query>` en `chatbot_consulta()`
- **Aviso de privacidad** visible en el widget de chatbot y en la pantalla de análisis de riesgo IA
- **Corrección de IDOR en apoderados**: vistas de detalle y edición ahora restringen acceso por rol
- **Corrección de IDOR en informes**: profesores solo pueden acceder a alumnos de sus propias asignaturas
- **Decorador centralizado `puede_ver_alumno`** aplicado de forma consistente en alumnos, anotaciones, asistencia y notas
- **Validación de imágenes con PIL** (comprobación de magic bytes) en subidas de foto de perfil, tanto en creación como en edición
- **Rate limiting en login** con `django-axes` (5 intentos fallidos → bloqueo por 1 hora)
- **`CSRF_COOKIE_HTTPONLY = True`** y **`SameSite = Strict`** aplicados a cookies de sesión y CSRF
- **Contraseñas mínimo 12 caracteres** configuradas via `MinimumLengthValidator`
- **Sanitización de comentarios en PDF** con `html.escape()` para prevenir inyección a través de ReportLab

### Rendimiento

- Índices de base de datos añadidos en `Alumno.curso`, `RegistroAsistencia.alumno` y `RegistroAsistencia.fecha`
- `UniqueConstraint` en `Nota` para evitar duplicados `(alumno, asignatura, tipo_evaluacion, fecha, descripcion)`
- `on_delete=PROTECT` en `Alumno.curso` para prevenir borrados accidentales de cursos con alumnos
- Corrección de queries N+1 en dashboard, vistas de alumnos e informes usando `select_related()`
- Paginación implementada en notificaciones (20/pág), anotaciones (30/pág) e historial (20/pág)
- `transaction.atomic()` en signals de recálculo de promedios para evitar race conditions
- Caché de 1 hora para resultado de `analizar_riesgo_alumno()` — evita llamadas repetidas a la API de Groq

### Refactoring

- `dashboard/views.py` dividido en funciones privadas por rol: `_dashboard_admin`, `_dashboard_profesor`, `_dashboard_apoderado`, `_dashboard_alumno`
- Lógica de recopilación de datos de informes extraída a `informes/services.py` como `InformeService.recopilar_datos(alumno, periodo)`
- Validadores reutilizables creados en `usuarios/validators.py`: `validar_rut` y `validar_nota`
- `validar_rut` registrado como validator en el campo `Usuario.rut` (validación automática en formularios y admin)
- Configuración de settings dividida en módulos por entorno: `base.py`, `development.py`, `production.py`, `testing.py`

### Infraestructura

- `ManifestStaticFilesStorage` habilitado en producción para cache busting con content hash
- **Pipeline CI/CD** con GitHub Actions: job `lint` (ruff) + job `test` (MySQL 8.0) en cada push y PR a `main`
- `requirements-dev.txt` con herramientas de desarrollo: pytest, pytest-django, coverage, ruff, pre-commit
- `pyproject.toml` con configuración centralizada de ruff (linter) y pytest
- `.pre-commit-config.yaml` con hooks: ruff, trailing-whitespace, debug-statements
- `RotatingFileHandler` para logs de producción: `logs/errores.log` (10 MB por archivo, 5 backups)
- `AXES_ENABLED = False` y `MD5PasswordHasher` en `settings/testing.py` para tests más rápidos

### Tests

- Suite de **37 tests** cubriendo: recálculo de promedios por señal, asistencia bulk, acceso por rol en apoderados y dashboard, generación de informes, y prevención de IDOR en alumnos
- Tests distribuidos en: `usuarios/tests.py`, `alumnos/tests.py`, `notas/tests.py`, `asistencia/tests.py`, `informes/tests.py`, `dashboard/tests.py`

### Documentación

- `SECURITY.md`: política de seguridad, datos enviados a Groq, checklist de producción
- `CONTRIBUTING.md`: guía completa de configuración, flujo de trabajo y convenciones
- `CLAUDE.md`: actualizado con settings por entorno, patrones de test, validadores y servicios

---

## [1.0.0] — 2026-01-15

Versión inicial funcional del sistema desplegado en Alwaysdata.

### Incluye

- Gestión completa de usuarios con cuatro roles: `admin`, `profesor`, `alumno`, `apoderado`
- Módulos: alumnos, profesores, apoderados, cursos, asignaturas, notas, asistencia, anotaciones
- Libro de notas con escala 1.0–7.0 y caché de promedios por señal Django
- Asistencia diaria con estados: Presente, Ausente, Atrasado, Justificado
- Generación de informes PDF individuales por alumno/período (ReportLab)
- Informes de ranking por curso e informe de fin de año
- Impresión masiva de PDF para curso completo (pypdf)
- Mensajería interna y envíos masivos a apoderados/profesores
- Historial de auditoría para cambios en notas y anotaciones
- Dashboard diferenciado por rol con métricas relevantes
- Análisis de riesgo académico mediante IA (Groq — llama-3.1-8b-instant)
- Chatbot pedagógico en dashboard para admin y profesores
- Interfaz responsiva con TailwindCSS 3.x, modo oscuro persistente
- Formulario de contacto con rate limiting básico
- Página institucional de presentación del colegio

---

[1.1.0]: https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE/releases/tag/v1.0.0
