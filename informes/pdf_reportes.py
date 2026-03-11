"""
APP: informes
ARCHIVO: pdf_reportes.py

Genera PDFs para:
  1. Informe por curso  → ranking de promedios, asistencia y anotaciones positivas
  2. Informe de fin de año → resumen anual por alumno con todos los períodos
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.platypus import Image as RLImage

# ── Paleta corporativa ──────────────────────────────────────────────────────
AZUL        = colors.HexColor('#197fe6')
AZUL_OSC    = colors.HexColor('#0d1b2a')
GRIS_LINEA  = colors.HexColor('#e2e8f0')
GRIS_TXT    = colors.HexColor('#6b7fa3')
VERDE       = colors.HexColor('#059669')
ROJO        = colors.HexColor('#dc2626')
AMARILLO    = colors.HexColor('#d97706')
MORADO      = colors.HexColor('#7c3aed')
BLANCO      = colors.white
FONDO_FILA  = colors.HexColor('#f8fafc')
FONDO_ALT   = colors.white
FONDO_HDR   = colors.HexColor('#eef2f7')


def _hex(c):
    h = c.hexval()
    return h.lstrip('#') if h.startswith('#') else h


def _seccion(texto, color=AZUL):
    st = ParagraphStyle('sec', fontSize=9, fontName='Helvetica-Bold',
                         textColor=BLANCO, leftIndent=0)
    t = Table([[Paragraph(texto, st)]], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), color),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    return KeepTogether([t, Spacer(1, 4)])


def _encabezado_pdf(story, titulo, subtitulo, logo_path, styles):
    """Encabezado común para todos los reportes."""
    # Logo
    if logo_path:
        try:
            col_logo = RLImage(logo_path, width=1.8*cm, height=1.8*cm)
        except Exception:
            col_logo = Paragraph('', styles['Normal'])
    else:
        col_logo = Paragraph('', styles['Normal'])

    col_colegio = [
        Paragraph('<font size="11" color="#0d1b2a"><b>Sistema de Gestión Escolar</b></font>',
                  ParagraphStyle('cn', fontSize=11, fontName='Helvetica-Bold', leading=14)),
        Paragraph('<font size="8" color="#6b7fa3">Rancagua, Chile  ·  contacto@colegio.cl</font>',
                  ParagraphStyle('cs', fontSize=8, leading=11)),
    ]
    col_titulo = [
        Paragraph(f'<b>{titulo}</b>',
                  ParagraphStyle('it', fontSize=14, fontName='Helvetica-Bold',
                                  textColor=AZUL_OSC, alignment=TA_CENTER, leading=18)),
        Paragraph(subtitulo,
                  ParagraphStyle('ip', fontSize=9, fontName='Helvetica',
                                  textColor=AZUL, alignment=TA_CENTER, leading=12)),
    ]
    ht = Table([[col_logo, col_colegio, col_titulo]], colWidths=[2.2*cm, 6.8*cm, 8*cm])
    ht.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING',(0,0), (-1,-1), 4),
    ]))
    story.append(ht)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width='100%', thickness=2, color=AZUL, spaceAfter=10))


# ══════════════════════════════════════════════════════════════════════════════
# 1. INFORME POR CURSO — ranking mejores promedios, asistencia y anotaciones
# ══════════════════════════════════════════════════════════════════════════════

def generar_pdf_ranking_curso(cursos_data, periodo, logo_path=None):
    """
    cursos_data: lista de dicts con estructura:
        {
          'curso': Curso,
          'alumnos': [
            {
              'alumno': Alumno,
              'promedio': float|None,
              'pct_asistencia': float,
              'positivas': int,
              'negativas': int,
            }, ...
          ]
        }
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Ranking por Curso - {periodo}",
    )
    styles = getSampleStyleSheet()
    story  = []

    _encabezado_pdf(story, 'RANKING POR CURSO', str(periodo), logo_path, styles)

    # Estilos de celda
    ST_HDR = ParagraphStyle('sh', fontSize=7.5, fontName='Helvetica-Bold',
                             textColor=BLANCO, alignment=TA_CENTER, leading=10)
    ST_N   = ParagraphStyle('sn', fontSize=8,   fontName='Helvetica',
                             textColor=AZUL_OSC, leading=10)
    ST_C   = ParagraphStyle('sc', fontSize=8,   fontName='Helvetica',
                             textColor=AZUL_OSC, alignment=TA_CENTER, leading=10)
    ST_MED = ParagraphStyle('sm', fontSize=9, fontName='Helvetica-Bold',
                             alignment=TA_CENTER, leading=12)

    for bloque in cursos_data:
        curso   = bloque['curso']
        alumnos = bloque['alumnos']

        story.append(_seccion(f'  {curso}', AZUL))

        if not alumnos:
            story.append(Paragraph('Sin alumnos registrados en este período.',
                                   ParagraphStyle('x', fontSize=8, textColor=GRIS_TXT)))
            story.append(Spacer(1, 8))
            continue

        # ── Tabla ranking ──────────────────────────────────────────────────
        # Ordenar por promedio desc
        alumnos_prom = sorted(
            [a for a in alumnos if a['promedio'] is not None],
            key=lambda x: x['promedio'], reverse=True
        )
        alumnos_sin  = [a for a in alumnos if a['promedio'] is None]
        ordenados    = alumnos_prom + alumnos_sin

        tabla_data = [[
            Paragraph('#',          ST_HDR),
            Paragraph('Alumno',     ST_HDR),
            Paragraph('Promedio',   ST_HDR),
            Paragraph('Asistencia', ST_HDR),
            Paragraph('Positivas',  ST_HDR),
            Paragraph('Negativas',  ST_HDR),
        ]]

        for i, row in enumerate(ordenados, 1):
            prom  = row['promedio']
            pct   = row['pct_asistencia']
            pos   = row['positivas']
            neg   = row['negativas']

            c_prom = VERDE if prom and prom >= 4.0 else (ROJO if prom else GRIS_TXT)
            c_asist = VERDE if pct >= 85 else (AMARILLO if pct >= 75 else ROJO)

            # Medalla para top 3
            medalla = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, str(i))

            tabla_data.append([
                Paragraph(medalla if i <= 3 else str(i), ST_C),
                Paragraph(row['alumno'].nombre_completo, ST_N),
                Paragraph(
                    f'<font color="#{_hex(c_prom)}"><b>{prom if prom else "—"}</b></font>',
                    ST_MED),
                Paragraph(
                    f'<font color="#{_hex(c_asist)}"><b>{pct}%</b></font>',
                    ST_MED),
                Paragraph(
                    f'<font color="#{_hex(VERDE)}"><b>{pos}</b></font>' if pos else '—',
                    ST_C),
                Paragraph(
                    f'<font color="#{_hex(ROJO)}"><b>{neg}</b></font>' if neg else '—',
                    ST_C),
            ])

        t = Table(tabla_data, colWidths=[1*cm, 6*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,0),  AZUL),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [FONDO_FILA, FONDO_ALT]),
            ('GRID',           (0,0), (-1,-1), 0.3, GRIS_LINEA),
            ('FONTSIZE',       (0,0), (-1,-1), 8),
            ('TOPPADDING',     (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',  (0,0), (-1,-1), 4),
            ('LEFTPADDING',    (0,0), (-1,-1), 6),
            ('RIGHTPADDING',   (0,0), (-1,-1), 6),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN',          (0,0), (0,-1),  'CENTER'),
            ('ALIGN',          (2,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t)

        # ── Mini resumen del curso ─────────────────────────────────────────
        promedios_validos = [a['promedio'] for a in alumnos if a['promedio']]
        prom_curso = round(sum(promedios_validos)/len(promedios_validos), 1) if promedios_validos else None
        pct_curso  = round(sum(a['pct_asistencia'] for a in alumnos)/len(alumnos), 1) if alumnos else 0
        tot_pos    = sum(a['positivas'] for a in alumnos)
        tot_neg    = sum(a['negativas'] for a in alumnos)

        ST_RES_LBL = ParagraphStyle('rl', fontSize=6.5, fontName='Helvetica-Bold',
                                     textColor=GRIS_TXT, alignment=TA_CENTER, leading=9)
        ST_RES_VAL = ParagraphStyle('rv', fontSize=10, fontName='Helvetica-Bold',
                                     alignment=TA_CENTER, leading=13)
        c_pc = VERDE if prom_curso and prom_curso >= 4.0 else ROJO
        c_pa = VERDE if pct_curso >= 85 else (AMARILLO if pct_curso >= 75 else ROJO)

        resumen = Table(
            [
                [Paragraph('PROMEDIO CURSO', ST_RES_LBL),
                 Paragraph('ASISTENCIA MEDIA', ST_RES_LBL),
                 Paragraph('TOTAL POSITIVAS', ST_RES_LBL),
                 Paragraph('TOTAL NEGATIVAS', ST_RES_LBL)],
                [Paragraph(f'<font color="#{_hex(c_pc)}"><b>{prom_curso or "—"}</b></font>', ST_RES_VAL),
                 Paragraph(f'<font color="#{_hex(c_pa)}"><b>{pct_curso}%</b></font>', ST_RES_VAL),
                 Paragraph(f'<font color="#{_hex(VERDE)}"><b>{tot_pos}</b></font>', ST_RES_VAL),
                 Paragraph(f'<font color="#{_hex(ROJO)}"><b>{tot_neg}</b></font>', ST_RES_VAL)],
            ],
            colWidths=[4.25*cm]*4,
        )
        resumen.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), FONDO_HDR),
            ('BOX',           (0,0), (-1,-1), 0.5, AZUL),
            ('LINEBEFORE',    (1,0), (-1,-1), 0.4, GRIS_LINEA),
            ('LINEBELOW',     (0,0), (-1,0),  0.4, GRIS_LINEA),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(Spacer(1, 4))
        story.append(resumen)
        story.append(Spacer(1, 14))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ══════════════════════════════════════════════════════════════════════════════
# 2. INFORME DE FIN DE AÑO — informe individual por alumno, un alumno por página
# ══════════════════════════════════════════════════════════════════════════════

def generar_pdf_fin_anio(alumnos_data, periodos, anio, logo_path=None):
    """
    Genera un PDF con una página por alumno.
    alumnos_data: lista de dicts:
        {
          'alumno': Alumno,
          'periodos': {
              periodo_id: {
                  'promedio': float|None,
                  'notas_por_asignatura': { nombre: {'promedio': float, 'notas': []} },
                  'asistencia_pct': float,
                  'asistencia_total': int,
                  'asistencia_presentes': int,
                  'asistencia_ausentes': int,
                  'positivas': int,
                  'negativas': int,
              }
          },
          'promedio_anual': float|None,
          'asistencia_anual': float,
          'positivas_total': int,
          'negativas_total': int,
        }
    periodos: lista de Periodo ordenados
    """
    import re as _re
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Informe Fin de Año {anio}",
    )
    styles  = getSampleStyleSheet()
    story   = []

    # ── Estilos reutilizables ──────────────────────────────────────────────
    LBL   = ParagraphStyle('lbl',  fontSize=6.5, fontName='Helvetica-Bold',
                            textColor=GRIS_TXT, leading=9)
    VAL   = ParagraphStyle('val',  fontSize=9,   fontName='Helvetica-Bold',
                            textColor=AZUL_OSC, leading=12)
    NRM   = ParagraphStyle('nrm',  fontSize=8.5, fontName='Helvetica',
                            textColor=AZUL_OSC, leading=12)
    CTR   = ParagraphStyle('ctr',  fontSize=8.5, fontName='Helvetica',
                            textColor=AZUL_OSC, leading=12, alignment=TA_CENTER)
    HDR   = ParagraphStyle('hdr',  fontSize=8,   fontName='Helvetica-Bold',
                            textColor=BLANCO,   leading=10, alignment=TA_CENTER)
    HDR_L = ParagraphStyle('hdrl', fontSize=8,   fontName='Helvetica-Bold',
                            textColor=BLANCO,   leading=10)
    BOLD  = ParagraphStyle('bld',  fontSize=8.5, fontName='Helvetica-Bold',
                            textColor=AZUL_OSC, leading=12)

    def _sec(texto, color=AZUL):
        t = Table([[Paragraph(texto, HDR_L)]], colWidths=[17*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), color),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        return KeepTogether([t, Spacer(1, 5)])

    first_page = True

    for row in alumnos_data:
        if not first_page:
            story.append(PageBreak())
        first_page = False

        alumno = row['alumno']
        import re as _re2
        curso_str    = str(alumno.curso) if alumno.curso else '—'
        curso_nombre = _re2.sub(r'\s*\(\d{4}\)\s*$', '', curso_str).strip()

        # ── ENCABEZADO ────────────────────────────────────────────────────
        if logo_path:
            try:    col_logo = RLImage(logo_path, width=1.8*cm, height=1.8*cm)
            except: col_logo = Paragraph('', styles['Normal'])
        else:
            col_logo = Paragraph('', styles['Normal'])

        col_colegio = [
            Paragraph('<font size="11" color="#0d1b2a"><b>Sistema de Gestión Escolar</b></font>',
                      ParagraphStyle('cn', fontSize=11, fontName='Helvetica-Bold', leading=14)),
            Paragraph('<font size="8" color="#6b7fa3">Rancagua, Chile  ·  contacto@colegio.cl</font>',
                      ParagraphStyle('cs', fontSize=8, leading=11)),
        ]
        col_titulo = [
            Paragraph('<b>INFORME ANUAL</b>',
                      ParagraphStyle('it', fontSize=16, fontName='Helvetica-Bold',
                                      textColor=AZUL_OSC, alignment=TA_CENTER, leading=20)),
            Paragraph(f'Año Escolar {anio}',
                      ParagraphStyle('ip', fontSize=10, fontName='Helvetica',
                                      textColor=AZUL, alignment=TA_CENTER, leading=13)),
        ]
        ht = Table([[col_logo, col_colegio, col_titulo]], colWidths=[2.2*cm, 6.8*cm, 8*cm])
        ht.setStyle(TableStyle([
            ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING',(0,0), (-1,-1), 4),
        ]))
        story.append(ht)
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width='100%', thickness=2, color=AZUL, spaceAfter=8))

        # ── DATOS DEL ALUMNO ──────────────────────────────────────────────
        campos = [
            ('NOMBRE',       alumno.nombre_completo),
            ('CURSO',        curso_nombre),
            ('RUT',          alumno.usuario.rut or '—'),
            ('N° MATRÍCULA', str(alumno.numero_matricula)),
            ('AÑO',          str(anio)),
        ]
        col_w = [6*cm, 2.5*cm, 3.0*cm, 2.5*cm, 2.5*cm]
        dt = Table(
            [[Paragraph(l, LBL) for l, _ in campos],
             [Paragraph(v, VAL) for _, v in campos]],
            colWidths=col_w, rowHeights=[0.42*cm, 0.6*cm]
        )
        dt.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BACKGROUND',    (0,0), (-1,0),  colors.HexColor('#eef2f7')),
            ('BOX',           (0,0), (-1,-1), 0.8, AZUL),
            ('LINEBEFORE',    (1,0), (-1,-1), 0.4, GRIS_LINEA),
            ('LINEBELOW',     (0,0), (-1,0),  0.4, GRIS_LINEA),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('RIGHTPADDING',  (0,0), (-1,-1), 8),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(dt)
        story.append(Spacer(1, 10))

        # ── RENDIMIENTO ACADÉMICO POR PERÍODO ─────────────────────────────
        story.append(_sec('RENDIMIENTO ACADÉMICO'))

        # Recopilar todas las asignaturas del año
        todas_asigs = set()
        for pid, pd in row['periodos'].items():
            todas_asigs.update(pd['notas_por_asignatura'].keys())
        todas_asigs = sorted(todas_asigs)

        if todas_asigs:
            # Cabecera: Asignatura | Período1 | Período2 | ... | Promedio Anual
            cab_ancho = [4.5*cm] + [round(10*cm/len(periodos), 2)]*len(periodos) + [2.5*cm]
            cab_hdr   = [Paragraph('Asignatura', HDR_L)]
            for p in periodos:
                cab_hdr.append(Paragraph(p.get_numero_display(), HDR))
            cab_hdr.append(Paragraph('Promedio\nAnual', HDR))

            tabla_notas = [cab_hdr]

            for asig in todas_asigs:
                fila_asig = [Paragraph(asig, NRM)]
                promedios_asig = []

                for p in periodos:
                    pd       = row['periodos'].get(p.pk, {})
                    asig_data = pd.get('notas_por_asignatura', {}).get(asig)
                    if asig_data and asig_data['promedio'] is not None:
                        prom_per = asig_data['promedio']
                        promedios_asig.append(prom_per)
                        c = VERDE if prom_per >= 4.0 else ROJO
                        fila_asig.append(Paragraph(
                            f'<font color="#{_hex(c)}" size="11"><b>{prom_per}</b></font>',
                            CTR))
                    else:
                        fila_asig.append(Paragraph('—', CTR))

                # Promedio anual de la asignatura
                prom_anual_asig = round(sum(promedios_asig)/len(promedios_asig), 1) if promedios_asig else None
                c_pa = VERDE if prom_anual_asig and prom_anual_asig >= 4.0 else (ROJO if prom_anual_asig else GRIS_TXT)
                fila_asig.append(Paragraph(
                    f'<font color="#{_hex(c_pa)}"><b>{prom_anual_asig or "—"}</b></font>',
                    ParagraphStyle('pa', fontSize=10, fontName='Helvetica-Bold', alignment=1, leading=13)
                ))
                tabla_notas.append(fila_asig)

            # Fila promedio general anual
            pa  = row['promedio_anual']
            c_pa = VERDE if pa and pa >= 4.0 else (ROJO if pa else GRIS_TXT)
            fila_pg = [Paragraph('<b>PROMEDIO GENERAL ANUAL</b>',
                                  ParagraphStyle('pg', fontSize=8.5, fontName='Helvetica-Bold',
                                                  textColor=AZUL_OSC, leading=11))]
            for p in periodos:
                pd_prom = row['periodos'].get(p.pk, {}).get('promedio')
                c = VERDE if pd_prom and pd_prom >= 4.0 else (ROJO if pd_prom else GRIS_TXT)
                fila_pg.append(Paragraph(
                    f'<font color="#{_hex(c)}"><b>{pd_prom or "—"}</b></font>',
                    ParagraphStyle('pgp', fontSize=10, fontName='Helvetica-Bold',
                                    alignment=1, leading=13)))
            fila_pg.append(Paragraph(
                f'<font color="#{_hex(c_pa)}" size="12"><b>{pa or "—"}</b></font>',
                ParagraphStyle('pga', fontSize=12, fontName='Helvetica-Bold',
                                alignment=1, leading=15)))
            tabla_notas.append(fila_pg)

            t_ac = Table(tabla_notas, colWidths=cab_ancho)
            t_ac.setStyle(TableStyle([
                ('BACKGROUND',     (0,0), (-1,0),  AZUL),
                ('ROWBACKGROUNDS', (0,1), (-1,-2), [FONDO_FILA, FONDO_ALT]),
                ('BACKGROUND',     (0,-1),(-1,-1), colors.HexColor('#eef6ff')),
                ('FONTNAME',       (0,-1),(-1,-1), 'Helvetica-Bold'),
                ('LINEABOVE',      (0,-1),(-1,-1), 1.5, AZUL),
                ('GRID',           (0,0), (-1,-1), 0.3, GRIS_LINEA),
                ('TOPPADDING',     (0,0), (-1,-1), 4),
                ('BOTTOMPADDING',  (0,0), (-1,-1), 4),
                ('LEFTPADDING',    (0,0), (-1,-1), 6),
                ('RIGHTPADDING',   (0,0), (-1,-1), 6),
                ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN',          (0,0), (0,-1),  'LEFT'),
                ('ALIGN',          (1,0), (-1,-1), 'CENTER'),
            ]))
            story.append(t_ac)
        else:
            story.append(Paragraph('Sin notas registradas en el año.',
                                   ParagraphStyle('x', fontSize=8, textColor=GRIS_TXT)))
        story.append(Spacer(1, 10))

        # ── ASISTENCIA ANUAL ──────────────────────────────────────────────
        story.append(_sec('ASISTENCIA'))

        # Tabla: una fila por período + fila total
        asist_hdr = [
            Paragraph('Período', HDR_L),
            Paragraph('Total Clases', HDR),
            Paragraph('Presentes', HDR),
            Paragraph('Ausentes', HDR),
            Paragraph('% Asistencia', HDR),
        ]
        asist_data = [asist_hdr]
        tot_total = tot_pres = tot_aus = 0

        for p in periodos:
            pd = row['periodos'].get(p.pk, {})
            tc  = pd.get('asistencia_total', 0)
            pr  = pd.get('asistencia_presentes', 0)
            au  = pd.get('asistencia_ausentes', 0)
            pct = pd.get('asistencia_pct', 0)
            tot_total += tc; tot_pres += pr; tot_aus += au
            c_a = VERDE if pct >= 85 else (AMARILLO if pct >= 75 else ROJO)
            asist_data.append([
                Paragraph(str(p), NRM),
                Paragraph(str(tc), CTR),
                Paragraph(str(pr), CTR),
                Paragraph(str(au), CTR),
                Paragraph(f'<font color="#{_hex(c_a)}"><b>{pct}%</b></font>',
                          ParagraphStyle('ap', fontSize=9, fontName='Helvetica-Bold',
                                          alignment=1, leading=12)),
            ])

        # Fila totales
        aa   = row['asistencia_anual']
        c_aa = VERDE if aa >= 85 else (AMARILLO if aa >= 75 else ROJO)
        asist_data.append([
            Paragraph('<b>TOTAL AÑO</b>',
                      ParagraphStyle('at', fontSize=8.5, fontName='Helvetica-Bold',
                                      textColor=AZUL_OSC, leading=11)),
            Paragraph(f'<b>{tot_total}</b>', ParagraphStyle('atv', fontSize=9,
                       fontName='Helvetica-Bold', alignment=1, leading=12)),
            Paragraph(f'<b>{tot_pres}</b>',  ParagraphStyle('atv2', fontSize=9,
                       fontName='Helvetica-Bold', alignment=1, leading=12)),
            Paragraph(f'<b>{tot_aus}</b>',   ParagraphStyle('atv3', fontSize=9,
                       fontName='Helvetica-Bold', alignment=1, leading=12)),
            Paragraph(f'<font color="#{_hex(c_aa)}"><b>{aa}%</b></font>',
                      ParagraphStyle('atp', fontSize=10, fontName='Helvetica-Bold',
                                      alignment=1, leading=13)),
        ])

        t_as = Table(asist_data, colWidths=[6*cm, 2.75*cm, 2.75*cm, 2.75*cm, 2.75*cm])
        t_as.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0),  AZUL),
            ('ROWBACKGROUNDS',(0,1), (-1,-2), [FONDO_FILA, FONDO_ALT]),
            ('BACKGROUND',    (0,-1),(-1,-1), colors.HexColor('#eef6ff')),
            ('LINEABOVE',     (0,-1),(-1,-1), 1.5, AZUL),
            ('FONTNAME',      (0,-1),(-1,-1), 'Helvetica-Bold'),
            ('GRID',          (0,0), (-1,-1), 0.3, GRIS_LINEA),
            ('TOPPADDING',    (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ('RIGHTPADDING',  (0,0), (-1,-1), 6),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_as)
        story.append(Spacer(1, 10))

        # ── ANOTACIONES ───────────────────────────────────────────────────
        pos_total = row['positivas_total']
        neg_total = row['negativas_total']

        if pos_total or neg_total:
            story.append(_sec('ANOTACIONES DEL AÑO'))
            anot_resumen = Table(
                [
                    [Paragraph('ANOTACIONES POSITIVAS', LBL),
                     Paragraph('ANOTACIONES NEGATIVAS', LBL)],
                    [Paragraph(f'<font color="#{_hex(VERDE)}" size="16"><b>{pos_total}</b></font>',
                               ParagraphStyle('apr', fontSize=16, fontName='Helvetica-Bold',
                                               alignment=1, leading=20)),
                     Paragraph(f'<font color="#{_hex(ROJO)}" size="16"><b>{neg_total}</b></font>',
                               ParagraphStyle('anr', fontSize=16, fontName='Helvetica-Bold',
                                               alignment=1, leading=20))],
                ],
                colWidths=[8.5*cm, 8.5*cm]
            )
            anot_resumen.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), FONDO_FILA),
                ('BOX',           (0,0), (-1,-1), 0.5, GRIS_LINEA),
                ('LINEBEFORE',    (1,0), (1,-1),  0.5, GRIS_LINEA),
                ('LINEBELOW',     (0,0), (-1,0),  0.5, GRIS_LINEA),
                ('TOPPADDING',    (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING',   (0,0), (-1,-1), 10),
                ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN',         (0,1), (-1,-1), 'CENTER'),
            ]))
            story.append(anot_resumen)
            story.append(Spacer(1, 10))

        # ── SITUACIÓN FINAL ───────────────────────────────────────────────
        story.append(_sec('SITUACIÓN FINAL', colors.HexColor('#1e40af')))

        pa      = row['promedio_anual']
        aa      = row['asistencia_anual']
        aprobado   = pa and pa >= 4.0
        promovido  = aprobado and aa >= 85
        c_aprobado = VERDE if aprobado  else ROJO
        c_promovido= VERDE if promovido else ROJO
        txt_apr    = 'APROBADO'    if aprobado  else 'REPROBADO'
        txt_prom   = 'PROMOVIDO'   if promovido else 'NO PROMOVIDO'

        sit_table = Table(
            [
                [Paragraph('PROMEDIO ANUAL', LBL),
                 Paragraph('ASISTENCIA ANUAL', LBL),
                 Paragraph('SITUACIÓN ACADÉMICA', LBL),
                 Paragraph('PROMOCIÓN DE CURSO', LBL)],
                [Paragraph(f'<font color="#{_hex(c_aprobado)}" size="14"><b>{pa or "—"}</b></font>',
                           ParagraphStyle('sv1', fontSize=14, fontName='Helvetica-Bold',
                                           alignment=1, leading=18)),
                 Paragraph(f'<font color="#{_hex(VERDE if aa >= 85 else AMARILLO if aa >= 75 else ROJO)}" size="14"><b>{aa}%</b></font>',
                           ParagraphStyle('sv2', fontSize=14, fontName='Helvetica-Bold',
                                           alignment=1, leading=18)),
                 Paragraph(f'<font color="#{_hex(c_aprobado)}" size="12"><b>{txt_apr}</b></font>',
                           ParagraphStyle('sv3', fontSize=12, fontName='Helvetica-Bold',
                                           alignment=1, leading=16)),
                 Paragraph(f'<font color="#{_hex(c_promovido)}" size="12"><b>{txt_prom}</b></font>',
                           ParagraphStyle('sv4', fontSize=12, fontName='Helvetica-Bold',
                                           alignment=1, leading=16)),
                ],
            ],
            colWidths=[3.5*cm, 3.5*cm, 5*cm, 5*cm]
        )
        sit_table.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), FONDO_FILA),
            ('BACKGROUND',    (0,0), (-1,0),  FONDO_HDR),
            ('BOX',           (0,0), (-1,-1), 1, colors.HexColor('#1e40af')),
            ('LINEBEFORE',    (1,0), (-1,-1), 0.5, GRIS_LINEA),
            ('LINEBELOW',     (0,0), (-1,0),  0.5, GRIS_LINEA),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN',         (0,1), (-1,-1), 'CENTER'),
        ]))
        story.append(sit_table)
        story.append(Spacer(1, 16))

        # ── FIRMAS ────────────────────────────────────────────────────────
        ST_FIR = ParagraphStyle('fir', fontSize=8, fontName='Helvetica',
                                 textColor=AZUL_OSC, alignment=TA_CENTER, leading=11)
        # Firmas: línea como guiones en Paragraph para evitar bug de HRFlowable en tabla
        linea_txt = Paragraph('_' * 28, ParagraphStyle('ln', fontSize=9,
                               textColor=AZUL_OSC, alignment=TA_CENTER, leading=12))
        def _firma(cargo):
            return [
                Spacer(1, 1.2*cm),
                Paragraph('_' * 28, ParagraphStyle('ln2', fontSize=9,
                           textColor=AZUL_OSC, alignment=TA_CENTER, leading=12)),
                Paragraph(cargo, ST_FIR),
            ]
        firmas = Table(
            [[_firma('Director(a)'), _firma('Profesor(a) Jefe'), _firma('Apoderado(a)')]],
            colWidths=[5.5*cm, 5.5*cm, 5.5*cm],
        )
        firmas.setStyle(TableStyle([
            ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',        (0,0), (-1,-1), 'BOTTOM'),
            ('TOPPADDING',    (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(firmas)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
