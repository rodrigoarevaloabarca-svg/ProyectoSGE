"""
APP: informes
ARCHIVO: pdf_generator.py

Genera el PDF del informe académico usando ReportLab.
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus import Image as RLImage

# ── Colores corporativos ──
AZUL_PRIMARY  = colors.HexColor('#197fe6')
AZUL_OSCURO   = colors.HexColor('#0d1b2a')
GRIS_CLARO    = colors.HexColor('#e2e8f0')
GRIS_TEXTO    = colors.HexColor('#6b7fa3')
VERDE         = colors.HexColor('#059669')
ROJO          = colors.HexColor('#dc2626')
AMARILLO      = colors.HexColor('#d97706')
BLANCO        = colors.white


def generar_pdf_informe(alumno, periodo, datos, comentario, logo_path=None):
    """
    Genera el PDF completo del informe académico.
    Retorna bytes del PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Informe {alumno.nombre_completo} - {periodo}",
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Estilos personalizados ──
    estilo_titulo = ParagraphStyle('titulo',
        parent=styles['Normal'],
        fontSize=22, fontName="Helvetica-Bold",
        textColor=AZUL_OSCURO, alignment=TA_CENTER, spaceBefore=0, spaceAfter=0, leading=28)

    estilo_subtitulo = ParagraphStyle('subtitulo',
        parent=styles['Normal'],
        fontSize=12, fontName="Helvetica",
        textColor=AZUL_PRIMARY, alignment=TA_CENTER, spaceBefore=0, spaceAfter=0, leading=16)

    estilo_seccion = ParagraphStyle('seccion',
        parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold',
        textColor=BLANCO, alignment=TA_LEFT)

    estilo_normal = ParagraphStyle('normal_custom',
        parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=AZUL_OSCURO, leading=14)

    estilo_comentario = ParagraphStyle('comentario',
        parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-Oblique',
        textColor=AZUL_OSCURO, leading=14,
        leftIndent=10, rightIndent=10)

    # ════════════════════════════════════════════════
    # ENCABEZADO
    # ════════════════════════════════════════════════
    header_data = []

    # ── Encabezado: logo pequeño + nombre colegio + título + datos alumno en una sola banda ──
    estilo_label = ParagraphStyle('label', fontSize=7, fontName='Helvetica-Bold',
                                   textColor=GRIS_TEXTO, leading=10)
    estilo_valor = ParagraphStyle('valor', fontSize=9, fontName='Helvetica-Bold',
                                   textColor=AZUL_OSCURO, leading=12)

    # Logo reducido
    if logo_path:
        try:
            col_logo = RLImage(logo_path, width=1.8*cm, height=1.8*cm)
        except Exception:
            col_logo = Paragraph('', styles['Normal'])
    else:
        col_logo = Paragraph('', styles['Normal'])

    # Nombre colegio + subtítulo
    col_colegio = [
        Paragraph('<font size="11" color="#0d1b2a"><b>Sistema de Gestión Escolar</b></font>',
                  ParagraphStyle('cn', fontSize=11, fontName='Helvetica-Bold', leading=14)),
        Paragraph('<font size="8" color="#6b7fa3">Rancagua, Chile  ·  contacto@colegio.cl</font>',
                  ParagraphStyle('cs', fontSize=8, leading=11)),
    ]

    # Título centrado
    col_titulo = [
        Paragraph('<b>INFORME ACADÉMICO</b>',
                  ParagraphStyle('it', fontSize=16, fontName='Helvetica-Bold',
                                  textColor=AZUL_OSCURO, alignment=TA_CENTER, leading=20)),
        Paragraph(str(periodo),
                  ParagraphStyle('ip', fontSize=10, fontName='Helvetica',
                                  textColor=AZUL_PRIMARY, alignment=TA_CENTER, leading=13)),
    ]

    header_table = Table([[col_logo, col_colegio, col_titulo]],
                          colWidths=[2.2*cm, 6.8*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING',(0,0), (-1,-1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width='100%', thickness=2, color=AZUL_PRIMARY, spaceAfter=8))

    # ════════════════════════════════════════════════
    # DATOS DEL ALUMNO — tarjetas uniformes
    # Cada campo = label gris arriba + valor negro abajo,
    # todos con exactamente el mismo tamaño y padding.
    # ════════════════════════════════════════════════

    # Estilos uniformes — UN solo tamaño para todo
    LBL = ParagraphStyle('lbl', fontSize=6.5, fontName='Helvetica-Bold',
                          textColor=GRIS_TEXTO, leading=9, spaceAfter=1)
    VAL = ParagraphStyle('val', fontSize=9, fontName='Helvetica-Bold',
                          textColor=AZUL_OSCURO, leading=12)

    # Período limpio: "1° Trimestre" sin año
    periodo_display = periodo.get_numero_display()  # "1° Trimestre" / "1° Semestre"

    import re as _re
    curso_str    = str(alumno.curso) if alumno.curso else '—'
    curso_nombre = _re.sub(r'\s*\(\d{4}\)\s*$', '', curso_str).strip()

    # 5 columnas de ancho equilibrado — total 17cm
    campos = [
        ('NOMBRE',       alumno.nombre_completo),   # 6cm
        ('CURSO',        curso_nombre),              # 2.5cm — sin año, cabe holgado
        ('RUT',          alumno.usuario.rut or '—'), # 3.0cm
        ('N° MATRÍCULA', str(alumno.numero_matricula)), # 2.5cm
        ('PERÍODO',      periodo_display),           # 2.5cm
    ]
    col_widths = [6.5*cm, 2.5*cm, 3.0*cm, 2.5*cm, 2.5*cm]

    fila_l = [Paragraph(lbl, LBL) for lbl, _ in campos]
    fila_v = [Paragraph(val, VAL) for _, val in campos]

    datos_table = Table(
        [fila_l, fila_v],
        colWidths=col_widths,
        rowHeights=[0.42*cm, 0.6*cm]
    )
    datos_table.setStyle(TableStyle([
        # Fondo uniforme
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        # Borde exterior
        ('BOX',           (0,0), (-1,-1), 0.8, AZUL_PRIMARY),
        # Separadores verticales entre celdas
        ('LINEBEFORE',    (1,0), (-1,-1), 0.4, GRIS_CLARO),
        # Línea entre label y valor
        ('LINEBELOW',     (0,0), (-1,0),  0.4, GRIS_CLARO),
        # Padding idéntico en todas las celdas
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(datos_table)
    story.append(Spacer(1, 10))

    # ════════════════════════════════════════════════
    # NOTAS POR ASIGNATURA
    # ════════════════════════════════════════════════
    story.append(_seccion_header('RENDIMIENTO ACADÉMICO', AZUL_PRIMARY))

    # ── Leyenda de tipos de evaluación usados en el período ──
    tipos_usados = {}
    for data in datos['notas_por_asignatura'].values():
        for n in data['notas']:
            tipo = n.tipo_evaluacion.nombre if n.tipo_evaluacion else '—'
            if tipo not in tipos_usados:
                tipos_usados[tipo] = n.tipo_evaluacion.porcentaje_ponderacion if n.tipo_evaluacion else None

    if tipos_usados:
        leyenda_items = []
        for tipo, pond in tipos_usados.items():
            if pond and pond != 100:
                leyenda_items.append(f'{tipo} ({pond}%)')
            else:
                leyenda_items.append(tipo)
        leyenda_txt = '  ·  '.join(leyenda_items)
        t_leyenda = Table(
            [[Paragraph(
                f'<font size="8" color="#6b7fa3"><b>Tipos de evaluación:</b>  {leyenda_txt}</font>',
                ParagraphStyle('leyenda', fontSize=8, leading=12)
            )]],
            colWidths=[17*cm]
        )
        t_leyenda.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('BOX',           (0,0), (-1,-1), 0.3, GRIS_CLARO),
        ]))
        story.append(t_leyenda)
        story.append(Spacer(1, 6))

    # Estilo uniforme para celdas de notas
    NOTA_LBL = ParagraphStyle('nl', fontSize=6.5, fontName='Helvetica',
                               textColor=GRIS_TEXTO, alignment=1, leading=8)
    NOTA_VAL = ParagraphStyle('nv', fontSize=9.5, fontName='Helvetica-Bold',
                               alignment=1, leading=12)

    notas_data = [
        [Paragraph('<b>Asignatura</b>', ParagraphStyle('h', fontSize=8, textColor=BLANCO, leading=10)),
         Paragraph('<b>Notas</b>',      ParagraphStyle('h', fontSize=8, textColor=BLANCO, leading=10, alignment=1)),
         Paragraph('<b>Promedio</b>',   ParagraphStyle('h', fontSize=8, textColor=BLANCO, leading=10, alignment=1)),
         Paragraph('<b>Estado</b>',     ParagraphStyle('h', fontSize=8, textColor=BLANCO, leading=10, alignment=1)),
        ]
    ]
    notas_por_asig = datos['notas_por_asignatura']

    if notas_por_asig:
        for nombre_asig, data in notas_por_asig.items():
            promedio   = data['promedio']
            color_prom = VERDE if promedio and promedio >= 4.0 else (ROJO if promedio else GRIS_TEXTO)
            estado     = 'Aprobado' if promedio and promedio >= 4.0 else ('Reprobado' if promedio else '—')

            # Mini tabla horizontal uniforme: tipo (label) / valor
            notas_cols = len(data['notas'])
            if notas_cols:
                cw = min(1.5*cm, 8.5*cm / notas_cols)
                t_inline = Table(
                    [
                        [Paragraph(
                            n.tipo_evaluacion.nombre if n.tipo_evaluacion else 'Nota',
                            NOTA_LBL) for n in data['notas']
                        ],
                        [Paragraph(
                            f'<font color="#{_hex(VERDE if float(n.valor)>=4.0 else ROJO)}">'
                            f'<b>{n.valor}</b></font>',
                            NOTA_VAL) for n in data['notas']
                        ],
                    ],
                    colWidths=[cw] * notas_cols,
                    rowHeights=[0.38*cm, 0.52*cm]
                )
                t_inline.setStyle(TableStyle([
                    ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                    ('LINEBELOW',     (0,0), (-1,0),  0.3, GRIS_CLARO),
                    ('TOPPADDING',    (0,0), (-1,-1), 1),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('LEFTPADDING',   (0,0), (-1,-1), 1),
                    ('RIGHTPADDING',  (0,0), (-1,-1), 1),
                ]))
                celda_notas = t_inline
            else:
                celda_notas = Paragraph('—', estilo_normal)

            notas_data.append([
                Paragraph(nombre_asig, ParagraphStyle('an', fontSize=8.5,
                          fontName='Helvetica', textColor=AZUL_OSCURO, leading=11)),
                celda_notas,
                Paragraph(f'<font color="#{_hex(color_prom)}" size="11"><b>{promedio or "—"}</b></font>',
                          ParagraphStyle('prom', fontSize=11, alignment=1, leading=14)),
                Paragraph(f'<font color="#{_hex(color_prom)}">{estado}</font>',
                          ParagraphStyle('est', fontSize=8, alignment=1, leading=11)),
            ])
    else:
        notas_data.append([Paragraph('Sin notas registradas en este período',
                           estilo_normal), '', '', ''])

    # Promedio general
    pg       = datos['promedio_general']
    color_pg = VERDE if pg and pg >= 4.0 else (ROJO if pg else GRIS_TEXTO)
    notas_data.append([
        Paragraph('<b>PROMEDIO GENERAL</b>',
                  ParagraphStyle('pg', fontSize=8.5, fontName='Helvetica-Bold',
                                  textColor=AZUL_OSCURO, leading=11)),
        '',
        Paragraph(f'<font color="#{_hex(color_pg)}" size="13"><b>{pg or "—"}</b></font>',
                  ParagraphStyle('pgv', fontSize=13, alignment=1, leading=16)),
        Paragraph(f'<font color="#{_hex(color_pg)}"><b>{"Aprobado" if pg and pg >= 4.0 else "Reprobado" if pg else "—"}</b></font>',
                  ParagraphStyle('pge', fontSize=8.5, fontName='Helvetica-Bold', alignment=1, leading=11)),
    ])

    t_notas = Table(notas_data, colWidths=[4*cm, 9.9*cm, 1.8*cm, 1.8*cm])
    t_notas.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  AZUL_PRIMARY),
        ('TEXTCOLOR',     (0,0), (-1,0),  BLANCO),
        ('ROWBACKGROUNDS',(0,1), (-1,-2), [colors.HexColor('#f8fafc'), BLANCO]),
        ('BACKGROUND',    (0,-1), (-1,-1), colors.HexColor('#eef6ff')),
        ('FONTNAME',      (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE',     (0,-1), (-1,-1), 1.5, AZUL_PRIMARY),
        ('TOPPADDING',    (0,0), (-1,0),  5),
        ('BOTTOMPADDING', (0,0), (-1,0),  5),
        ('TOPPADDING',    (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 7),
        ('RIGHTPADDING',  (0,0), (-1,-1), 7),
        ('GRID',          (0,0), (-1,-1), 0.3, GRIS_CLARO),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN',         (0,0), (0,-1),  'LEFT'),
        ('ALIGN',         (1,0), (-1,-1), 'CENTER'),
        ('SPAN',          (1,-1), (1,-1)),
    ]))
    story.append(t_notas)
    story.append(Spacer(1, 14))

    # ════════════════════════════════════════════════
    # ASISTENCIA
    # ════════════════════════════════════════════════
    story.append(_seccion_header('ASISTENCIA', AZUL_PRIMARY))

    asist = datos['asistencia']
    pct   = asist['porcentaje']
    color_asist = VERDE if pct >= 85 else (AMARILLO if pct >= 70 else ROJO)

    asist_data = [
        ['Total clases', 'Presentes', 'Ausentes', 'Atrasados', 'Justificados', '% Asistencia'],
        [
            str(asist['total']),
            str(asist['presentes']),
            str(asist['ausentes']),
            str(asist['atrasados']),
            str(asist['justificados']),
            Paragraph(f'<font color="#{_hex(color_asist)}" size="12"><b>{pct}%</b></font>', 
                     ParagraphStyle('c', alignment=TA_CENTER, fontSize=12)),
        ]
    ]
    t_asist = Table(asist_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3.5*cm])
    t_asist.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), AZUL_PRIMARY),
        ('TEXTCOLOR',     (0,0), (-1,0), BLANCO),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.HexColor('#f8fafc')]),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.3, GRIS_CLARO),
    ]))
    story.append(t_asist)
    story.append(Spacer(1, 14))

    # ════════════════════════════════════════════════
    # ANOTACIONES
    # ════════════════════════════════════════════════
    story.append(_seccion_header('ANOTACIONES DEL PERÍODO', AZUL_PRIMARY))

    positivas = list(datos['positivas'])
    negativas = list(datos['negativas'])

    if not positivas and not negativas:
        story.append(Paragraph('Sin anotaciones en este período.', estilo_normal))
    else:
        if positivas:
            story.append(Paragraph(
                f'<font color="#059669"><b>Positivas ({len(positivas)})</b></font>',
                estilo_normal))
            story.append(Spacer(1, 4))
            anot_data = [['Fecha', 'Descripción', 'Registrado por']]
            for a in positivas:
                anot_data.append([
                    str(a.fecha),
                    Paragraph(a.descripcion[:100], estilo_normal),
                    a.creado_por.get_full_name() if a.creado_por else '—',
                ])
            story.append(_tabla_anotaciones(anot_data, VERDE))
            story.append(Spacer(1, 8))

        if negativas:
            story.append(Paragraph(
                f'<font color="#dc2626"><b>Negativas ({len(negativas)})</b></font>',
                estilo_normal))
            story.append(Spacer(1, 4))
            anot_data = [['Fecha', 'Descripción', 'Registrado por']]
            for a in negativas:
                anot_data.append([
                    str(a.fecha),
                    Paragraph(a.descripcion[:100], estilo_normal),
                    a.creado_por.get_full_name() if a.creado_por else '—',
                ])
            story.append(_tabla_anotaciones(anot_data, ROJO))

    story.append(Spacer(1, 14))

    # ════════════════════════════════════════════════
    # COMENTARIO DEL PROFESOR
    # ════════════════════════════════════════════════
    if comentario and comentario.strip():
        story.append(_seccion_header('COMENTARIO DEL PROFESOR', AZUL_PRIMARY))
        story.append(Spacer(1, 6))
        t_com = Table(
            [[Paragraph(comentario, estilo_comentario)]],
            colWidths=[17*cm]
        )
        t_com.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#f0f9ff')),
            ('LEFTPADDING',   (0,0), (-1,-1), 12),
            ('RIGHTPADDING',  (0,0), (-1,-1), 12),
            ('TOPPADDING',    (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LINEBEFORETABLE', (0,0), (0,-1), 3, AZUL_PRIMARY),
            ('BOX',           (0,0), (-1,-1), 0.5, GRIS_CLARO),
        ]))
        story.append(t_com)
        story.append(Spacer(1, 14))

    # ════════════════════════════════════════════════
    # FIRMA
    # ════════════════════════════════════════════════
    story.append(Spacer(1, 20))
    firma_data = [
        ['_______________________', '_______________________', '_______________________'],
        ['Profesor Jefe', 'Director(a)', 'Apoderado'],
        ['Nombre y firma', 'Nombre y firma', 'Nombre y firma'],
    ]
    t_firma = Table(firma_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    t_firma.setStyle(TableStyle([
        ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME',    (1,0), (1,2),   'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 8),
        ('TEXTCOLOR',   (0,0), (-1,-1), GRIS_TEXTO),
        ('TOPPADDING',  (0,0), (-1,-1), 4),
    ]))
    story.append(t_firma)

    # ── Pie de página con fecha ──
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRIS_CLARO))
    from django.utils import timezone as tz
    story.append(Paragraph(
        f'<font size="7" color="#6b7fa3">Documento generado el {tz.now().strftime("%d/%m/%Y %H:%M")} | Sistema de Gestión Escolar — Confidencial</font>',
        ParagraphStyle('pie', alignment=TA_CENTER, fontSize=7)
    ))

    doc.build(story)
    return buffer.getvalue()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _seccion_header(texto, color):
    """Genera una barra de sección con fondo de color."""
    t = Table(
        [[Paragraph(f'<font color="white"><b>{texto}</b></font>',
                    ParagraphStyle('sh', fontSize=10, fontName='Helvetica-Bold',
                                   textColor=colors.white, leading=14))]],
        colWidths=[17*cm]
    )
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), color),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROUNDEDCORNERS', [4]),
    ]))
    return KeepTogether([t, Spacer(1, 6)])


def _tabla_anotaciones(data, color_header):
    t = Table(data, colWidths=[2.5*cm, 10*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), color_header),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.HexColor('#fafafa'), colors.white]),
        ('GRID',          (0,0), (-1,-1), 0.3, GRIS_CLARO),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ]))
    return t


def _hex(color_obj):
    """Extrae hex string de un color ReportLab sin el #."""
    h = color_obj.hexval()
    return h.lstrip('#') if h.startswith('#') else h
