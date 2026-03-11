"""
APP: informes
ARCHIVO: views.py
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone

from .models import Periodo, ComentarioInforme
from .pdf_generator import generar_pdf_informe
from .forms import PeriodoForm, ComentarioInformeForm
from alumnos.models import Alumno
from cursos.models import Curso


def _solo_admin_o_profesor(user):
    return user.es_admin or user.es_profesor


# ── PERÍODOS ────────────────────────────────────────────────────────────────

@login_required
def lista_periodos(request):
    if not _solo_admin_o_profesor(request.user):
        return redirect('dashboard:inicio')
    periodos = Periodo.objects.all()
    return render(request, 'informes/lista_periodos.html', {'periodos': periodos,
        'breadcrumbs': [{'label': 'Centro de Informes', 'url': '/informes/dashboard/'}, {'label': 'Períodos Académicos', 'url': ''}]})


@login_required
def crear_periodo(request):
    if not request.user.es_admin:
        messages.error(request, 'Solo el administrador puede crear períodos.')
        return redirect('informes:lista_periodos')
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Período creado exitosamente.')
            return redirect('informes:lista_periodos')
    else:
        form = PeriodoForm()
    return render(request, 'informes/form_periodo.html', {'form': form, 'titulo': 'Crear Período'})


@login_required
def editar_periodo(request, pk):
    if not request.user.es_admin:
        return redirect('informes:lista_periodos')
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Período actualizado.')
            return redirect('informes:lista_periodos')
    else:
        form = PeriodoForm(instance=periodo)
    return render(request, 'informes/form_periodo.html', {'form': form, 'titulo': 'Editar Período'})


# ── INFORMES ─────────────────────────────────────────────────────────────────

@login_required
def seleccionar_informe(request):
    """Paso 1: elegir período y alumno/curso."""
    if not _solo_admin_o_profesor(request.user):
        return redirect('dashboard:inicio')

    periodos = Periodo.objects.filter(activo=True)
    cursos   = Curso.objects.all()
    alumnos  = Alumno.objects.filter(activo=True).select_related('usuario', 'curso')

    # Filtrar por curso si se selecciona
    curso_id = request.GET.get('curso')
    if curso_id:
        alumnos = alumnos.filter(curso_id=curso_id)

    return render(request, 'informes/seleccionar.html', {
        'breadcrumbs': [{'label': 'Centro de Informes', 'url': '/informes/dashboard/'}, {'label': 'Informe Individual', 'url': ''}],
        'periodos': periodos,
        'cursos':   cursos,
        'alumnos':  alumnos,
        'curso_id': curso_id,
    })


@login_required
def ver_informe(request, alumno_id, periodo_id):
    """Paso 2: ver el informe en pantalla con opción de agregar comentario."""
    if not _solo_admin_o_profesor(request.user):
        return redirect('dashboard:inicio')

    alumno  = get_object_or_404(Alumno, pk=alumno_id)
    periodo = get_object_or_404(Periodo, pk=periodo_id)

    datos = _recopilar_datos_informe(alumno, periodo)

    # Comentario existente o nuevo
    comentario_obj, _ = ComentarioInforme.objects.get_or_create(
        alumno=alumno, periodo=periodo,
        defaults={'profesor': request.user}
    )

    if request.method == 'POST':
        form = ComentarioInformeForm(request.POST, instance=comentario_obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profesor = request.user
            obj.save()
            messages.success(request, 'Comentario guardado.')
            return redirect('informes:ver_informe', alumno_id=alumno_id, periodo_id=periodo_id)
    else:
        form = ComentarioInformeForm(instance=comentario_obj)

    return render(request, 'informes/ver_informe.html', {
        'breadcrumbs': [{'label': 'Centro de Informes', 'url': '/informes/dashboard/'}, {'label': 'Informe Individual', 'url': '/informes/'}, {'label': alumno.nombre_completo, 'url': ''}],
        'alumno':       alumno,
        'periodo':      periodo,
        'datos':        datos,
        'form':         form,
        'comentario':   comentario_obj,
    })


@login_required
def descargar_pdf(request, alumno_id, periodo_id):
    """Genera y descarga el PDF del informe."""
    if not _solo_admin_o_profesor(request.user):
        return redirect('dashboard:inicio')

    alumno  = get_object_or_404(Alumno, pk=alumno_id)
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    datos   = _recopilar_datos_informe(alumno, periodo)

    comentario_obj = ComentarioInforme.objects.filter(alumno=alumno, periodo=periodo).first()
    comentario_texto = comentario_obj.comentario if comentario_obj else ''

    # Logo del colegio (si existe)
    import os
    from django.conf import settings
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo_colegio.png')
    if not os.path.exists(logo_path):
        logo_path = None

    pdf_bytes = generar_pdf_informe(alumno, periodo, datos, comentario_texto, logo_path)

    nombre_archivo = f"informe_{alumno.usuario.last_name}_{periodo}.pdf".replace(' ', '_')
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


# ── HELPER ───────────────────────────────────────────────────────────────────

def _recopilar_datos_informe(alumno, periodo):
    """Recopila notas, asistencia y anotaciones del alumno en el período."""
    from notas.models import Nota
    from asistencia.models import RegistroAsistencia
    from anotaciones.models import Anotacion

    fecha_i = periodo.fecha_inicio
    fecha_f = periodo.fecha_fin

    # ── Notas del período ──
    notas_qs = Nota.objects.filter(
        alumno=alumno,
        fecha__gte=fecha_i,
        fecha__lte=fecha_f,
    ).select_related('asignatura', 'tipo_evaluacion').order_by('asignatura__nombre', 'fecha')

    # Agrupar notas por asignatura
    notas_por_asignatura = {}
    for nota in notas_qs:
        nombre_asig = nota.asignatura.nombre
        if nombre_asig not in notas_por_asignatura:
            notas_por_asignatura[nombre_asig] = {
                'asignatura': nota.asignatura,
                'notas': [],
                'promedio': None,
            }
        notas_por_asignatura[nombre_asig]['notas'].append(nota)

    # Calcular promedio por asignatura en el período
    for key, data in notas_por_asignatura.items():
        valores = [float(n.valor) for n in data['notas']]
        data['promedio'] = round(sum(valores) / len(valores), 1) if valores else None

    # Promedio general del período
    todos_promedios = [d['promedio'] for d in notas_por_asignatura.values() if d['promedio']]
    promedio_general = round(sum(todos_promedios) / len(todos_promedios), 1) if todos_promedios else None

    # ── Asistencia del período ──
    asistencias = RegistroAsistencia.objects.filter(
        alumno=alumno,
        fecha__gte=fecha_i,
        fecha__lte=fecha_f,
    )
    total_clases  = asistencias.count()
    presentes     = asistencias.filter(estado='presente').count()
    ausentes      = asistencias.filter(estado='ausente').count()
    atrasados     = asistencias.filter(estado='atrasado').count()
    justificados  = asistencias.filter(estado='justificado').count()
    pct_asistencia = round((presentes / total_clases * 100), 1) if total_clases > 0 else 0

    # ── Anotaciones del período ──
    anotaciones = Anotacion.objects.filter(
        alumno=alumno,
        fecha__gte=fecha_i,
        fecha__lte=fecha_f,
    ).select_related('creado_por', 'asignatura').order_by('fecha')

    positivas = anotaciones.filter(tipo='positiva')
    negativas = anotaciones.filter(tipo='negativa')

    return {
        'notas_por_asignatura': notas_por_asignatura,
        'promedio_general':     promedio_general,
        'asistencia': {
            'total':        total_clases,
            'presentes':    presentes,
            'ausentes':     ausentes,
            'atrasados':    atrasados,
            'justificados': justificados,
            'porcentaje':   pct_asistencia,
        },
        'anotaciones':  anotaciones,
        'positivas':    positivas,
        'negativas':    negativas,
    }


# ── INFORME POR CURSO ─────────────────────────────────────────────────────────

@login_required
def informe_ranking_curso(request):
    """Seleccionar año → genera PDF ranking por curso (todos los períodos del año)."""
    if not _solo_admin_o_profesor(request.user):
        return redirect('dashboard:inicio')

    from django.utils import timezone as tz
    anios = Periodo.objects.values_list('anio', flat=True).distinct().order_by('-anio')
    anio_sel = int(request.GET.get('anio', tz.now().year))
    periodos_anio = Periodo.objects.filter(anio=anio_sel).order_by('tipo', 'numero')

    if request.GET.get('descargar'):
        return _descargar_ranking(request, anio_sel)

    return render(request, 'informes/ranking_curso.html', {
        'breadcrumbs': [{'label': 'Centro de Informes', 'url': '/informes/dashboard/'}, {'label': 'Ranking por Curso', 'url': ''}],
        'anios':        anios,
        'anio_sel':     anio_sel,
        'periodos_anio': periodos_anio,
    })


def _descargar_ranking(request, anio):
    import os
    from django.conf import settings
    from notas.models import Nota
    from asistencia.models import RegistroAsistencia
    from anotaciones.models import Anotacion
    from cursos.models import Curso
    from alumnos.models import Alumno
    from .pdf_reportes import generar_pdf_ranking_curso

    # Todos los períodos del año
    periodos_anio = list(Periodo.objects.filter(anio=anio).order_by('tipo', 'numero'))
    if not periodos_anio:
        messages.error(request, f'No hay períodos creados para el año {anio}.')
        return redirect('informes:ranking_curso')

    # Rango completo del año: desde el primer período al último
    fecha_inicio = min(p.fecha_inicio for p in periodos_anio)
    fecha_fin    = max(p.fecha_fin    for p in periodos_anio)

    cursos  = Curso.objects.all().order_by('nivel', 'grado', 'letra')
    cursos_data = []

    for curso in cursos:
        alumnos = Alumno.objects.filter(curso=curso, activo=True).select_related('usuario')
        if not alumnos.exists():
            continue

        filas = []
        for alumno in alumnos:
            notas = Nota.objects.filter(
                alumno=alumno,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin,
            )
            valores = [float(n.valor) for n in notas]
            promedio = round(sum(valores)/len(valores), 1) if valores else None

            asist = RegistroAsistencia.objects.filter(
                alumno=alumno,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin,
            )
            total = asist.count()
            presentes = asist.filter(estado='presente').count()
            pct = round(presentes/total*100, 1) if total else 0

            anot = Anotacion.objects.filter(
                alumno=alumno,
                fecha__gte=fecha_inicio,
                fecha__lte=fecha_fin,
            )
            filas.append({
                'alumno':          alumno,
                'promedio':        promedio,
                'pct_asistencia':  pct,
                'positivas':       anot.filter(tipo='positiva').count(),
                'negativas':       anot.filter(tipo='negativa').count(),
            })

        cursos_data.append({'curso': curso, 'alumnos': filas})

    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo_colegio.png')
    if not os.path.exists(logo_path):
        logo_path = None

    # Etiqueta del PDF: "Año completo 2026"
    class _Label:
        def __str__(self): return f'Año Completo {anio}'
    label = _Label()

    pdf_bytes = generar_pdf_ranking_curso(cursos_data, label, logo_path)
    nombre = f"ranking_cursos_{anio}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return response


# ── INFORME FIN DE AÑO ────────────────────────────────────────────────────────

@login_required
def informe_fin_anio(request):
    """Seleccionar año y períodos → genera PDF resumen anual."""
    if not _solo_admin_o_profesor(request.user):
        return redirect('dashboard:inicio')

    from django.utils import timezone
    anio_actual = timezone.now().year
    anios = Periodo.objects.values_list('anio', flat=True).distinct().order_by('-anio')

    anio_sel     = int(request.GET.get('anio', anio_actual))
    periodos_anio = Periodo.objects.filter(anio=anio_sel).order_by('tipo', 'numero')

    # Períodos seleccionados (checkboxes)
    ids_sel = request.GET.getlist('periodos')

    if request.GET.get('descargar') and ids_sel:
        return _descargar_fin_anio(request, anio_sel, ids_sel)

    return render(request, 'informes/fin_anio.html', {
        'breadcrumbs': [{'label': 'Centro de Informes', 'url': '/informes/dashboard/'}, {'label': 'Informe Fin de Año', 'url': ''}],
        'anios':        anios,
        'anio_sel':     anio_sel,
        'periodos_anio': periodos_anio,
        'ids_sel':      ids_sel,
    })


def _descargar_fin_anio(request, anio, ids_sel):
    import os
    from django.conf import settings
    from notas.models import Nota
    from asistencia.models import RegistroAsistencia
    from anotaciones.models import Anotacion
    from alumnos.models import Alumno
    from .pdf_reportes import generar_pdf_fin_anio

    periodos = list(Periodo.objects.filter(pk__in=ids_sel).order_by('tipo', 'numero'))
    alumnos  = Alumno.objects.filter(activo=True).select_related('usuario', 'curso').order_by('curso', 'usuario__last_name')

    alumnos_data = []
    for alumno in alumnos:
        resumen_periodos = {}
        promedios_validos = []
        pcts = []
        total_pos = 0
        total_neg = 0

        for periodo in periodos:
            # ── Notas con detalle por asignatura ──
            notas_qs = Nota.objects.filter(
                alumno=alumno,
                fecha__gte=periodo.fecha_inicio,
                fecha__lte=periodo.fecha_fin,
            ).select_related('asignatura', 'tipo_evaluacion').order_by('asignatura__nombre', 'fecha')

            notas_por_asig = {}
            for nota in notas_qs:
                nombre_asig = nota.asignatura.nombre
                if nombre_asig not in notas_por_asig:
                    notas_por_asig[nombre_asig] = {'notas': [], 'promedio': None}
                notas_por_asig[nombre_asig]['notas'].append(nota)
            for key, data in notas_por_asig.items():
                vals = [float(n.valor) for n in data['notas']]
                data['promedio'] = round(sum(vals)/len(vals), 1) if vals else None

            todos_prom = [d['promedio'] for d in notas_por_asig.values() if d['promedio']]
            prom = round(sum(todos_prom)/len(todos_prom), 1) if todos_prom else None
            if prom:
                promedios_validos.append(prom)

            # ── Asistencia ──
            asist = RegistroAsistencia.objects.filter(
                alumno=alumno,
                fecha__gte=periodo.fecha_inicio,
                fecha__lte=periodo.fecha_fin,
            )
            total    = asist.count()
            presentes = asist.filter(estado='presente').count()
            ausentes  = asist.filter(estado='ausente').count()
            pct = round(presentes/total*100, 1) if total else 0
            pcts.append(pct)

            # ── Anotaciones ──
            anot = Anotacion.objects.filter(
                alumno=alumno,
                fecha__gte=periodo.fecha_inicio,
                fecha__lte=periodo.fecha_fin,
            )
            pos = anot.filter(tipo='positiva').count()
            neg = anot.filter(tipo='negativa').count()
            total_pos += pos
            total_neg += neg

            resumen_periodos[periodo.pk] = {
                'promedio':               prom,
                'notas_por_asignatura':   notas_por_asig,
                'asistencia_pct':         pct,
                'asistencia_total':       total,
                'asistencia_presentes':   presentes,
                'asistencia_ausentes':    ausentes,
                'positivas':              pos,
                'negativas':              neg,
            }

        promedio_anual   = round(sum(promedios_validos)/len(promedios_validos), 1) if promedios_validos else None
        asistencia_anual = round(sum(pcts)/len(pcts), 1) if pcts else 0

        alumnos_data.append({
            'alumno':           alumno,
            'periodos':         resumen_periodos,
            'promedio_anual':   promedio_anual,
            'asistencia_anual': asistencia_anual,
            'positivas_total':  total_pos,
            'negativas_total':  total_neg,
        })

    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo_colegio.png')
    if not os.path.exists(logo_path):
        logo_path = None

    pdf_bytes = generar_pdf_fin_anio(alumnos_data, periodos, anio, logo_path)
    nombre = f"informe_anual_{anio}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return response


# ── DASHBOARD CENTRAL DE INFORMES ─────────────────────────────────────────────

@login_required
def dashboard_informes(request):
    """Hub central con acceso a todos los tipos de informe."""
    if not request.user.es_admin:
        return redirect('dashboard:inicio')

    from django.utils import timezone as tz
    periodos_activos = Periodo.objects.filter(activo=True).order_by('tipo', 'numero')
    total_periodos   = Periodo.objects.count()
    anio_actual      = tz.now().year
    periodos_anio    = Periodo.objects.filter(anio=anio_actual).count()

    from alumnos.models import Alumno
    from cursos.models import Curso
    total_alumnos = Alumno.objects.filter(activo=True).count()
    total_cursos  = Curso.objects.count()

    return render(request, 'informes/dashboard_informes.html', {
        'breadcrumbs': [{'label': 'Centro de Informes', 'url': ''}],
        'periodos_activos': periodos_activos,
        'total_periodos':   total_periodos,
        'periodos_anio':    periodos_anio,
        'total_alumnos':    total_alumnos,
        'total_cursos':     total_cursos,
        'anio_actual':      anio_actual,
    })


# ── IMPRESIÓN MASIVA POR CURSO ─────────────────────────────────────────────────

@login_required
def impresion_masiva(request):
    """Seleccionar curso + período → PDF con todos los alumnos del curso."""
    if not request.user.es_admin:
        return redirect('dashboard:inicio')

    from cursos.models import Curso
    periodos = Periodo.objects.all().order_by('-anio', 'tipo', 'numero')
    cursos   = Curso.objects.all().order_by('nivel', 'grado', 'letra')

    if request.GET.get('descargar'):
        curso_id   = request.GET.get('curso')
        periodo_id = request.GET.get('periodo')
        tipo       = request.GET.get('tipo', 'periodo')  # 'periodo' o 'anual'

        if not curso_id:
            messages.error(request, 'Selecciona un curso.')
            return redirect('informes:impresion_masiva')

        if tipo == 'anual':
            ids_sel = request.GET.getlist('periodos_anio')
            if not ids_sel:
                messages.error(request, 'Selecciona al menos un período para el informe anual.')
                return redirect('informes:impresion_masiva')
            return _impresion_masiva_anual(request, int(curso_id), ids_sel)
        else:
            if not periodo_id:
                messages.error(request, 'Selecciona un período.')
                return redirect('informes:impresion_masiva')
            return _impresion_masiva_periodo(request, int(curso_id), int(periodo_id))

    # Años disponibles para informe anual
    from django.utils import timezone as tz
    anios = Periodo.objects.values_list('anio', flat=True).distinct().order_by('-anio')
    anio_sel = int(request.GET.get('anio', tz.now().year))
    periodos_anio = Periodo.objects.filter(anio=anio_sel).order_by('tipo', 'numero')

    return render(request, 'informes/impresion_masiva.html', {
        'breadcrumbs': [{'label': 'Centro de Informes', 'url': '/informes/dashboard/'}, {'label': 'Impresión Masiva', 'url': ''}],
        'periodos':      periodos,
        'cursos':        cursos,
        'anios':         anios,
        'anio_sel':      anio_sel,
        'periodos_anio': periodos_anio,
        'curso_id':      request.GET.get('curso', ''),
        'periodo_id':    request.GET.get('periodo', ''),
        'ids_sel':       request.GET.getlist('periodos_anio'),
    })


def _impresion_masiva_periodo(request, curso_id, periodo_id):
    """PDF masivo: todos los alumnos del curso en un período — una página por alumno."""
    import os, io
    from django.conf import settings
    from alumnos.models import Alumno
    from cursos.models import Curso
    from .pdf_generator import generar_pdf_informe
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, PageBreak
    import io as _io

    curso   = get_object_or_404(Curso, pk=curso_id)
    periodo = get_object_or_404(Periodo, pk=periodo_id)
    alumnos = Alumno.objects.filter(curso=curso, activo=True).select_related('usuario').order_by('usuario__last_name')

    if not alumnos.exists():
        messages.error(request, f'No hay alumnos activos en {curso}.')
        return redirect('informes:impresion_masiva')

    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo_colegio.png')
    if not os.path.exists(logo_path):
        logo_path = None

    # Generar PDFs individuales y combinarlos con pypdf
    try:
        from pypdf import PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfMerger as _Merger
            merger = _Merger()
            for alumno in alumnos:
                datos = _recopilar_datos_informe(alumno, periodo)
                comentario_obj = ComentarioInforme.objects.filter(alumno=alumno, periodo=periodo).first()
                comentario_txt = comentario_obj.comentario if comentario_obj else ''
                pdf_bytes = generar_pdf_informe(alumno, periodo, datos, comentario_txt, logo_path)
                merger.append(_io.BytesIO(pdf_bytes))
            buffer = _io.BytesIO()
            merger.write(buffer)
            merger.close()
            buffer.seek(0)
        except ImportError:
            # Fallback: concatenar bytes crudos no es válido — usar reportlab para merge
            from reportlab.platypus import SimpleDocTemplate
            # Sin pypdf/PyPDF2 generamos un único PDF pasando todos los alumnos
            from .pdf_reportes import generar_pdf_fin_anio as _gen_masivo
            # Reutilizamos el generador de fin de año pero con un solo período
            ids_sel_fake = [str(periodo.pk)]
            return _impresion_masiva_anual(request, curso_id, ids_sel_fake)
    else:
        writer = PdfWriter()
        for alumno in alumnos:
            datos = _recopilar_datos_informe(alumno, periodo)
            comentario_obj = ComentarioInforme.objects.filter(alumno=alumno, periodo=periodo).first()
            comentario_txt = comentario_obj.comentario if comentario_obj else ''
            pdf_bytes = generar_pdf_informe(alumno, periodo, datos, comentario_txt, logo_path)
            from pypdf import PdfReader
            reader = PdfReader(_io.BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)
        buffer = _io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)

    import re as _re
    curso_clean = _re.sub(r'\s*\(\d{4}\)\s*$', '', str(curso)).replace(' ', '_')
    nombre = f"informes_{curso_clean}_{periodo}.pdf".replace(' ', '_')
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return response


def _impresion_masiva_anual(request, curso_id, ids_sel):
    """PDF masivo anual: todos los alumnos del curso — informe de fin de año."""
    import os
    from django.conf import settings
    from alumnos.models import Alumno
    from cursos.models import Curso
    from notas.models import Nota
    from asistencia.models import RegistroAsistencia
    from anotaciones.models import Anotacion
    from .pdf_reportes import generar_pdf_fin_anio

    curso   = get_object_or_404(Curso, pk=curso_id)
    periodos = list(Periodo.objects.filter(pk__in=ids_sel).order_by('tipo', 'numero'))
    alumnos  = Alumno.objects.filter(curso=curso, activo=True).select_related('usuario', 'curso').order_by('usuario__last_name')

    if not alumnos.exists():
        messages.error(request, f'No hay alumnos activos en {curso}.')
        return redirect('informes:impresion_masiva')

    anio = periodos[0].anio if periodos else timezone.now().year
    alumnos_data = []

    for alumno in alumnos:
        resumen_periodos  = {}
        promedios_validos = []
        pcts = []
        total_pos = total_neg = 0

        for periodo in periodos:
            notas_qs = Nota.objects.filter(
                alumno=alumno, fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_fin,
            ).select_related('asignatura', 'tipo_evaluacion').order_by('asignatura__nombre', 'fecha')

            notas_por_asig = {}
            for nota in notas_qs:
                na = nota.asignatura.nombre
                notas_por_asig.setdefault(na, {'notas': [], 'promedio': None})['notas'].append(nota)
            for key, data in notas_por_asig.items():
                vals = [float(n.valor) for n in data['notas']]
                data['promedio'] = round(sum(vals)/len(vals), 1) if vals else None

            todos_prom = [d['promedio'] for d in notas_por_asig.values() if d['promedio']]
            prom = round(sum(todos_prom)/len(todos_prom), 1) if todos_prom else None
            if prom: promedios_validos.append(prom)

            asist    = RegistroAsistencia.objects.filter(alumno=alumno, fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_fin)
            total    = asist.count()
            presentes = asist.filter(estado='presente').count()
            ausentes  = asist.filter(estado='ausente').count()
            pct = round(presentes/total*100, 1) if total else 0
            pcts.append(pct)

            anot = Anotacion.objects.filter(alumno=alumno, fecha__gte=periodo.fecha_inicio, fecha__lte=periodo.fecha_fin)
            pos  = anot.filter(tipo='positiva').count()
            neg  = anot.filter(tipo='negativa').count()
            total_pos += pos; total_neg += neg

            resumen_periodos[periodo.pk] = {
                'promedio': prom, 'notas_por_asignatura': notas_por_asig,
                'asistencia_pct': pct, 'asistencia_total': total,
                'asistencia_presentes': presentes, 'asistencia_ausentes': ausentes,
                'positivas': pos, 'negativas': neg,
            }

        alumnos_data.append({
            'alumno':           alumno,
            'periodos':         resumen_periodos,
            'promedio_anual':   round(sum(promedios_validos)/len(promedios_validos), 1) if promedios_validos else None,
            'asistencia_anual': round(sum(pcts)/len(pcts), 1) if pcts else 0,
            'positivas_total':  total_pos,
            'negativas_total':  total_neg,
        })

    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo_colegio.png')
    if not os.path.exists(logo_path):
        logo_path = None

    pdf_bytes = generar_pdf_fin_anio(alumnos_data, periodos, anio, logo_path)
    import re as _re
    curso_clean = _re.sub(r'\s*\(\d{4}\)\s*$', '', str(curso)).replace(' ', '_')
    nombre = f"informe_anual_{curso_clean}_{anio}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return response
