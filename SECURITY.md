# Política de Seguridad — SGE

## Reportar una vulnerabilidad

Para reportar una vulnerabilidad de seguridad, enviar un correo a:
**rodrigoarevaloabarca@gmail.com**

Incluir: descripción del problema, pasos para reproducirlo, impacto potencial.
No publicar vulnerabilidades en issues públicos sin coordinación previa.

## Versiones soportadas

| Componente | Versión | Soporte hasta |
|---|---|---|
| Django | 6.0.x LTS | Abril 2028 |
| Python | 3.10+ | Octubre 2026 |

## Advertencia sobre `.env`

El archivo `.env` local contiene credenciales de desarrollo. **Nunca** commitear
este archivo. Está excluido por `.gitignore`. Si alguna vez se expuso en git
history, rotar inmediatamente: `SECRET_KEY`, `GROQ_API_KEY`, `DB_PASSWORD`.

## Integración con Groq API (IA)

Las funciones `analizar_riesgo_alumno()` y `chatbot_consulta()` en `SGE/ia_utils.py`
envían datos académicos **anonimizados** (IDs numéricos) a la API de Groq. No se
envían nombres, RUTs ni datos de contacto. Al usar estas funciones, el usuario
acepta que datos académicos anonimizados son procesados por un servicio externo.

## Configuraciones de seguridad en producción

- `DEBUG=False` obligatorio
- `SECURE_SSL_REDIRECT=True` — forzar HTTPS
- `SECURE_HSTS_SECONDS=31536000` — HSTS por 1 año
- `SESSION_COOKIE_SECURE=True` — cookies solo por HTTPS
- `CSRF_COOKIE_SECURE=True` — CSRF cookie solo por HTTPS
- Login bloqueado tras 5 intentos fallidos (django-axes)
- Contraseñas mínimo 12 caracteres

## Datos sensibles

Este sistema maneja datos de menores de edad (alumnos de colegio). Cumplir
con la Ley 19.628 de Protección de Datos Personales (Chile). No exponer
datos personales (RUT, nombre, dirección) en logs ni en APIs externas.
