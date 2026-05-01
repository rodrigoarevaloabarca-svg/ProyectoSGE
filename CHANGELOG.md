# Changelog — SGE

Todos los cambios notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).
Versionado según [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.2.0] — 2026-05-01

Ronda de hardening de autenticación y auditoría de seguridad. Sin cambios de ruptura en la API ni en las funcionalidades existentes.

### Seguridad

- **Autenticación de dos factores (2FA)** con `django-otp`: soporte TOTP (Google Authenticator, Authy). Enrollment en `/usuarios/2fa/`. El panel `/admin/` requiere 2FA si el usuario tiene un dispositivo enrollado; si no, permite acceso para completar el enrollment.
- **Email con restricción `UNIQUE`**: campo `email` ahora es único a nivel de base de datos. Emails vacíos se almacenan como `NULL` (no cadena vacía) para permitir múltiples usuarios sin correo.
- **Tiempo de bloqueo de axes aumentado**: `AXES_COOLOFF_TIME` de 1 h a 3 h (antes podía forzarse en ~5 min/ciclo, ahora requiere esperar 3 h entre ataques).
- **Ruta `/accounts/login/` eliminada**: ya no existe el endpoint duplicado. El único login es `/usuarios/login/`.
- **`CambioContrasenaView` personalizada**: registra el evento en `HistorialCambio` y en el logger `sge.seguridad`. `update_session_auth_hash()` ya era llamado por Django internamente; ahora queda explícitamente documentado.
- **`ResetContrasenaView` con throttle**: cooldown de 120 segundos entre solicitudes de reset de contraseña por sesión. Loguea el email solicitado.
- **Señales de autenticación** (`usuarios/signals.py`): login exitoso y logout crean registros en `HistorialCambio`; login fallido se loguea como WARNING (axes ya lo persiste en su tabla propia).
- **Perfil editable para todos los roles**: profesores, alumnos y apoderados ahora pueden editar sus propios datos básicos (nombre, email, RUT, teléfono, foto). Corrección: el form de subida de foto ahora incluye `enctype="multipart/form-data"`.

### Auditoría

- **`HistorialCambio` extendido** con nuevos tipos de modelo (`usuario`) y acciones: `login`, `logout`, `login_fallido`, `cambio_contrasena`, `cambio_rol`, `desactivacion`.
- **Auditoría en `editar_usuario`**: cuando un admin cambia el rol de un usuario, el cambio queda registrado con estado anterior y posterior.
- **Auditoría en `desactivar_usuario`**: la desactivación de una cuenta crea un registro en historial.
- **`registrar_evento_usuario()`** en `historial/utils.py`: nueva función auxiliar para registrar eventos de seguridad asociados a un usuario.

### Infraestructura

- **`logs/seguridad.log`** en producción: nuevo archivo de log dedicado a eventos de seguridad, rotativo (5 MB, 10 backups). Logger `sge.seguridad` al nivel `WARNING`.
- **Creación automática del directorio `logs/`** al arrancar en producción (`os.makedirs(..., exist_ok=True)`).
- **`django-otp 1.7.0`** y **`qrcode 8.2`** añadidos a `requirements.txt`.
- Migraciones generadas: `usuarios/0002_email_unique.py`, `usuarios/0003_email_unique_nullable.py`, `historial/0002_alter_historialcambio_accion_and_more.py`.

### Documentación

- `README.md`: stack, tabla de características, tabla de permisos (todos los roles pueden editar su perfil y configurar 2FA), guía de enrollment 2FA en producción.
- `SECURITY.md`: sección de 2FA, tabla de medidas actualizada, checklist extendido.
- `CONTRIBUTING.md`: sección de auditoría y señales actualizada, nuevas variables de entorno.
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

[1.2.0]: https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE/releases/tag/v1.0.0
