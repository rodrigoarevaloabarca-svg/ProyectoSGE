# Política de Seguridad — SGE

## Reportar una vulnerabilidad

Para reportar una vulnerabilidad de seguridad, enviar un correo a:
**rodrigoarevaloabarca@gmail.com**

Incluir en el reporte:
- Descripción del problema
- Pasos para reproducirlo
- Impacto potencial (qué datos o funciones se ven comprometidos)
- Versión o commit afectado

**No publicar vulnerabilidades en issues públicos** sin coordinación previa con el mantenedor. Se responderá dentro de 72 horas con un plan de acción.

---

## Versiones soportadas

| Componente | Versión | Soporte hasta |
|---|---|---|
| SGE | 1.2.x | Activo |
| Django | 6.0.x | Abril 2028 |
| Python | 3.10+ | Octubre 2026 |
| MySQL | 8.0+ | Abril 2028 |

---

## Advertencia sobre `.env`

El archivo `.env` local contiene credenciales de desarrollo. **Nunca** hacer commit de este archivo. Está excluido en `.gitignore`. Si alguna vez se expuso en el historial de git, rotar inmediatamente:

- `SECRET_KEY`
- `GROQ_API_KEY`
- `DB_PASSWORD`
- `EMAIL_HOST_PASSWORD`

Para verificar si se expuso:
```bash
git log --all --full-history -- .env
git grep SECRET_KEY $(git log --format="%H")
```

---

## Integración con Groq API (IA)

Las funciones `analizar_riesgo_alumno()` y `chatbot_consulta()` en `SGE/ia_utils.py` envían datos académicos **anonimizados** a la API de Groq. La anonimización aplica antes de cualquier llamada a la API:

| Dato real | Dato enviado a Groq |
|---|---|
| Nombre del alumno | `ESTUDIANTE_{id}` |
| Nombre del curso | `CURSO_{id}` |
| Nombre de la asignatura | `ASIG_{id}` |
| RUT | *(no se envía)* |
| Dirección | *(no se envía)* |
| Teléfono | *(no se envía)* |

Los IDs internos son re-mapeados a nombres reales en el código antes de mostrar la respuesta al usuario. Groq nunca recibe información de identificación personal.

Al usar las funciones de IA, el usuario acepta que datos académicos anonimizados son procesados por un servicio externo (Groq, LLC). Ver la [política de privacidad de Groq](https://groq.com/privacy-policy).

---

## Protección contra prompt injection

La entrada del usuario en el chatbot está encapsulada con delimitadores explícitos antes de enviarse al modelo:

```python
user_content = f"<user_query>{pregunta}</user_query>"
```

Esto previene que texto malicioso en la pregunta del usuario redefina el comportamiento del sistema.

---

## Configuraciones de seguridad en producción

Obligatorias al desplegar en producción:

```env
DEBUG=False
SECRET_KEY=<clave aleatoria de mínimo 50 caracteres>
ALLOWED_HOSTS=<dominio real>
CSRF_TRUSTED_ORIGINS=https://<dominio real>
```

Django settings de producción (`SGE/settings/production.py`):

| Configuración | Valor | Propósito |
|---|---|---|
| `SECURE_SSL_REDIRECT` | `True` | Redirige HTTP → HTTPS |
| `SECURE_PROXY_SSL_HEADER` | `('HTTP_X_FORWARDED_PROTO', 'https')` | Funciona detrás de proxy inverso |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS por 1 año |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` | Cubre todos los subdominios |
| `SECURE_HSTS_PRELOAD` | `True` | Permite preload en navegadores |
| `SESSION_COOKIE_SECURE` | `True` | Cookies de sesión solo por HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | CSRF cookie solo por HTTPS |
| `CSRF_COOKIE_HTTPONLY` | `True` | CSRF no accesible por JavaScript |
| `CSRF_COOKIE_SAMESITE` | `'Strict'` | Previene CSRF cross-site |
| `SESSION_COOKIE_SAMESITE` | `'Strict'` | Previene session fixation cross-site |
| `X_FRAME_OPTIONS` | `'DENY'` | Previene clickjacking |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | Previene MIME sniffing |
| `SECURE_BROWSER_XSS_FILTER` | `True` | Activa filtro XSS del navegador |

---

## Medidas de seguridad implementadas

### Autenticación y autorización

- **2FA TOTP** (`django-otp`): enrollment disponible para todos los usuarios en `/usuarios/2fa/`. El panel `/admin/` requiere verificación OTP si hay un dispositivo enrollado.
- `django-axes`: bloqueo tras 5 intentos fallidos de login durante **3 horas**
- Contraseñas con mínimo 12 caracteres y validadores de complejidad de Django
- Sesión expira al cerrar el navegador (`SESSION_EXPIRE_AT_BROWSER_CLOSE = True`)
- `update_session_auth_hash()` preserva la sesión activa al cambiar contraseña, invalidando las demás
- Control de acceso por rol en todas las vistas (decoradores `solo_admin`, `solo_admin_o_profesor`)
- Email con `UNIQUE` constraint en base de datos; emails vacíos almacenados como `NULL`

### IDOR (Insecure Direct Object Reference)

- Decorador `@puede_ver_alumno` valida que el usuario tiene derecho a acceder al alumno en la URL
- Profesores solo ven alumnos de sus propias asignaturas
- Apoderados solo ven a sus pupilos registrados
- Alumnos solo ven su propio perfil

### Inyección y XSS

- ORM de Django con queries parametrizadas — sin SQL crudo en vistas
- `html.escape()` en comentarios de informes antes de renderizar con ReportLab
- CSRF habilitado globalmente (middleware `CsrfViewMiddleware`)

### Subida de archivos

- Validación de magic bytes con PIL (verifica que el archivo sea realmente una imagen)
- Límite de 2 MB por archivo de foto de perfil
- Solo se aceptan extensiones: `.jpg`, `.jpeg`, `.png`, `.webp`

### Rate limiting

- Login: `django-axes` (5 intentos → 3 horas de bloqueo)
- Formulario de contacto: cooldown de 60 segundos por sesión
- Reset de contraseña: cooldown de 120 segundos entre solicitudes por sesión

### Auditoría y trazabilidad

Los siguientes eventos quedan registrados en `HistorialCambio` **y** en `logs/seguridad.log`:

| Evento | Nivel de log | En historial DB |
|--------|:------------:|:---------------:|
| Login exitoso | INFO | ✅ |
| Logout | INFO | ✅ |
| Login fallido | WARNING | ❌ (axes lo persiste) |
| Cambio de contraseña | WARNING | ✅ |
| Cambio de rol | WARNING | ✅ |
| Desactivación de cuenta | WARNING | ✅ |

El archivo `logs/seguridad.log` se crea automáticamente y rota en 5 MB (10 backups).

---

## Datos sensibles y cumplimiento

Este sistema maneja datos de menores de edad (alumnos de colegio chileno). Es responsabilidad del operador del sistema cumplir con:

- **Ley 19.628** — Protección de la Vida Privada (Chile)
- **Ley 20.529** — Sistema Nacional de Aseguramiento de la Calidad de la Educación

Principios a respetar:
- No exponer RUT, nombre, dirección ni datos de contacto en logs
- No enviar datos personales a APIs externas sin anonimizar
- Limitar el acceso a datos académicos según el rol del usuario
- Mantener registros de auditoría para cambios en notas y anotaciones

---

## Checklist de despliegue seguro

Antes de poner en producción, verificar:

- [ ] `DEBUG=False` en el entorno de producción
- [ ] `SECRET_KEY` diferente a la de desarrollo, mínimo 50 caracteres
- [ ] `ALLOWED_HOSTS` configurado solo con el dominio real
- [ ] `CSRF_TRUSTED_ORIGINS` configurado con `https://` explícito
- [ ] Base de datos MySQL con usuario dedicado (sin `GRANT ALL` global)
- [ ] Certificado SSL válido instalado en el servidor web
- [ ] Archivos estáticos servidos por Nginx/Apache, no por Django
- [ ] Carpeta `media/` fuera de la raíz pública o acceso controlado
- [ ] Archivo `.env` con permisos `600` (`chmod 600 .env`)
- [ ] `GROQ_API_KEY` rotada si alguna vez estuvo en el historial de git
- [ ] Directorio `logs/` con permisos de escritura para el proceso WSGI (se crea automáticamente, verificar que no falle)
- [ ] **2FA enrollado por el administrador** antes de abrir acceso a terceros (ir a Mi Perfil → Activar 2FA)
- [ ] `python manage.py check --deploy` sin errores críticos
