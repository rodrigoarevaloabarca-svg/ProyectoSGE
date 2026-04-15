"""
SGE/ia_utils.py
Utilidades para integración con Groq API (gratuita).
"""
from groq import Groq
from django.conf import settings


def analizar_riesgo_alumno(alumno):
    promedio        = alumno.get_promedio_general()
    asistencia      = alumno.get_porcentaje_asistencia()
    promedios_asig  = alumno.get_promedio_por_asignatura()
    anotaciones_neg = alumno.anotaciones.filter(tipo='negativa').count()
    anotaciones_pos = alumno.anotaciones.filter(tipo='positiva').count()

    if promedio is None and asistencia is None:
        return None

    detalle_asignaturas = ""
    for asig, prom in promedios_asig.items():
        if prom is not None:
            estado = "reprobado" if prom < 4.0 else "aprobado"
            detalle_asignaturas += f"  - {asig.nombre}: {prom} ({estado})\n"

    prompt = f"""Eres un asistente pedagógico de un colegio chileno.
Analiza el riesgo académico del siguiente alumno y entrega un diagnóstico breve.

DATOS DEL ALUMNO:
- Nombre: {alumno.nombre_completo}
- Curso: {alumno.curso}
- Promedio general: {promedio if promedio else 'Sin notas'}
- Porcentaje de asistencia: {asistencia if asistencia else 'Sin registros'}%
- Anotaciones positivas: {anotaciones_pos}
- Anotaciones negativas: {anotaciones_neg}

PROMEDIOS POR ASIGNATURA:
{detalle_asignaturas if detalle_asignaturas else '  Sin notas registradas aún'}

INSTRUCCIONES:
1. Determina el nivel de riesgo: ALTO, MEDIO o BAJO
2. Explica brevemente por qué (2 oraciones máximo)
3. Da UNA recomendación concreta para el profesor

Responde en español, de forma clara y profesional. Máximo 5 líneas."""

    client = Groq(api_key=settings.GROQ_API_KEY)
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return respuesta.choices[0].message.content


def _buscar_contexto_bd(pregunta, usuario):
    """
    Busca en la BD informacion relevante segun la pregunta.
    Filtra los datos según el rol del usuario (IDOR fix).
    Anonimiza la información enviando IDs en lugar de nombres (Privacy fix).
    Retorna (contexto_string, map_nombres)
    """
    from alumnos.models import Alumno
    from cursos.models import Curso

    contexto = ""
    map_nombres = {}
    pregunta_lower = pregunta.lower()

    # Base queryset (siempre activo=True)
    qs_alumnos = Alumno.objects.filter(activo=True)
    qs_cursos = Curso.objects.filter(activo=True)

    # Restringir por permisos del profesor
    if usuario and not usuario.es_admin and usuario.es_profesor:
        qs_alumnos = qs_alumnos.filter(curso__asignaturas__profesor=usuario.perfil_profesor).distinct()
        qs_cursos = qs_cursos.filter(asignaturas__profesor=usuario.perfil_profesor).distinct()

    # Filtrar directamente en BD usando palabras de la pregunta (> 3 chars)
    palabras = [p for p in pregunta_lower.split() if len(p) > 3]
    if palabras:
        from django.db.models import Q
        filtro = Q()
        for palabra in palabras:
            filtro |= Q(usuario__first_name__icontains=palabra)
            filtro |= Q(usuario__last_name__icontains=palabra)

        alumnos_encontrados = qs_alumnos.filter(
            filtro
        ).select_related('usuario', 'curso')[:3]  # maximo 3 resultados

        if alumnos_encontrados.exists():
            contexto += "DATOS REALES DE LA BASE DE DATOS:\n\n"
            for alumno in alumnos_encontrados:
                anon_id = f"ESTUDIANTE_{alumno.pk}"
                map_nombres[anon_id] = alumno.nombre_completo

                promedio   = alumno.get_promedio_general()
                asistencia = alumno.get_porcentaje_asistencia()
                anot_neg   = alumno.anotaciones.filter(tipo='negativa').count()
                anot_pos   = alumno.anotaciones.filter(tipo='positiva').count()

                contexto += f"Alumno: {anon_id}\n"
                contexto += f"  Curso: {alumno.curso}\n"
                contexto += f"  Promedio general: {promedio if promedio else 'Sin notas'}\n"
                contexto += f"  Asistencia: {asistencia if asistencia else 'Sin registros'}%\n"
                contexto += f"  Anotaciones positivas: {anot_pos}\n"
                contexto += f"  Anotaciones negativas: {anot_neg}\n"

                promedios = alumno.get_promedio_por_asignatura()
                if promedios:
                    contexto += "  Notas por asignatura:\n"
                    for asig, prom in promedios.items():
                        if prom is not None:
                            estado = "reprobado" if prom < 4.0 else "aprobado"
                            contexto += f"    - {asig.nombre}: {prom} ({estado})\n"
                contexto += "\n"

    # Si pregunta por curso completo (ej: "3ro B", "4to A")
    for curso in qs_cursos:
        nombre_curso = str(curso).lower()
        if nombre_curso in pregunta_lower or any(
            p in pregunta_lower for p in nombre_curso.split() if len(p) > 2
        ):
            alumnos_curso = qs_alumnos.filter(
                curso=curso
            ).select_related('usuario')

            if alumnos_curso.exists():
                contexto += f"ALUMNOS DEL CURSO {curso}:\n"
                for a in alumnos_curso:
                    anon_id = f"ESTUDIANTE_{a.pk}"
                    map_nombres[anon_id] = a.nombre_completo
                    prom = a.get_promedio_general()
                    asis = a.get_porcentaje_asistencia()
                    contexto += f"  - {anon_id}: "
                    contexto += f"promedio {prom if prom else 'sin notas'}, "
                    contexto += f"asistencia {asis if asis else 'sin registros'}%\n"
                contexto += "\n"
            break

    return contexto, map_nombres


def chatbot_consulta(pregunta, usuario, historial=None):
    """
    Responde preguntas consultando primero la BD para obtener
    datos reales de alumnos y cursos anonimizados.
    """
    if historial is None:
        historial = []

    # Buscar datos relevantes en la BD (anonimizados)
    contexto_bd, map_nombres = _buscar_contexto_bd(pregunta, usuario)

    sistema = """Eres un asistente del Sistema de Gestión Escolar (SGE) 
de un colegio chileno. Ayudas a administradores y profesores respondiendo 
preguntas sobre alumnos, notas, asistencia y anotaciones.
Cuando tengas datos reales de la base de datos, úsalos para responder con precisión.
Responde siempre en español, de forma breve y profesional.
Si no encuentras información de un alumno específico, dilo claramente."""

    # Construir el mensaje con contexto de BD si existe
    contenido_usuario = pregunta
    if contexto_bd:
        contenido_usuario = f"{contexto_bd}\nPregunta del usuario: {pregunta}"

    mensajes = [{"role": "system", "content": sistema}]
    mensajes += historial
    mensajes.append({"role": "user", "content": contenido_usuario})

    client = Groq(api_key=settings.GROQ_API_KEY)
    respuesta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=mensajes,
        max_tokens=400
    )
    respuesta_final = respuesta.choices[0].message.content

    # Re-mapear los IDs anonimizados a los nombres reales
    for anon_id, nombre_real in map_nombres.items():
        respuesta_final = respuesta_final.replace(anon_id, nombre_real)

    return respuesta_final
