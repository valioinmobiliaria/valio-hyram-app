"""
Generador de Reportes Técnicos Oficiales en PDF — HyRAM+ Web
Desarrollado para Grupo VALIO S.A.S. (www.grupovalio.com)
Utiliza ReportLab y Matplotlib para generar informes ejecutivos full-color.
"""

import io
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.pdfgen import canvas


def sanitize_formula_for_pdf(text: str) -> str:
    """Convierte subíndices unicode a etiquetas HTML <sub> para ReportLab."""
    replacements = {
        'H₂': 'H<sub>2</sub>',
        'CH₄': 'CH<sub>4</sub>',
        'C₃H₈': 'C<sub>3</sub>H<sub>8</sub>',
        'CO₂': 'CO<sub>2</sub>',
        'm²': 'm<sup>2</sup>',
        '₂': '<sub>2</sub>',
        '₃': '<sub>3</sub>',
        '₄': '<sub>4</sub>',
        '₈': '<sub>8</sub>',
        '²': '<sup>2</sup>'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numeración 'Página X de Y' con pie de página limpio."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748b"))

        # Línea decorativa superior
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Encabezado corriente
        header_text = "GRUPO VALIO | Consultoria en Seguridad de Procesos & PPAM | HyRAM+ v6.1"
        self.drawString(36, 11 * inch - 25, header_text)

        # Línea decorativa inferior
        self.line(36, 38, 8.5 * inch - 36, 38)

        # Pie de página corriente limpio (sin caracteres Unicode no admitidos)
        footer_text = "Documento tecnico preliminar. Sujeto a clausula de responsabilidad."
        self.drawString(36, 26, footer_text)
        page_str = f"Pagina {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 36, 26, page_str)

        self.restoreState()


def generate_footprint_image(distances: dict, flame_length: float) -> io.BytesIO:
    """Genera la gráfica 2D de isocontornos de radiación térmica en alta resolución."""
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=220)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')

    d_16 = distances.get(1600)
    d_47 = distances.get(4700)
    d_98 = distances.get(9800)
    d_25 = distances.get(25000)

    # Elipses concéntricas representativas del chorro
    def add_zone_patch(dist, color, label, alpha=0.35):
        if dist and dist > 0:
            width = dist * 2.0
            height = dist * 1.3
            center_x = dist * 0.4
            ell = Ellipse(xy=(center_x, 0), width=width, height=height,
                          edgecolor=color, facecolor=color, alpha=alpha,
                          linewidth=1.8, label=label)
            ax.add_patch(ell)

    add_zone_patch(d_16, '#10b981', 'Zona Segura (1.6 kW/m2)', alpha=0.20)
    add_zone_patch(d_47, '#f59e0b', 'Escape Rapido (4.7 kW/m2)', alpha=0.28)
    add_zone_patch(d_98, '#f97316', 'Dano a Equipos (9.8 kW/m2)', alpha=0.38)
    add_zone_patch(d_25, '#ef4444', 'Critico / Llama (25 kW/m2)', alpha=0.50)

    # Vector de llama
    ax.plot([0, flame_length], [0, 0], color='#38bdf8', linestyle='--', linewidth=2.5,
            label=f'Llama Visible ({flame_length:.2f} m)', marker='o', markersize=4)

    # Punto de origen
    ax.scatter([0], [0], color='#ffffff', s=60, marker='X', zorder=5, label='Origen de Fuga (0,0)')

    # Determinar límites
    max_x = max([d for d in [d_16, d_47, d_98, d_25, flame_length] if d is not None] + [5.0]) * 1.25
    ax.set_xlim(-max_x * 0.25, max_x)
    ax.set_ylim(-max_x * 0.55, max_x * 0.55)

    ax.set_title("Huella 2D de Isocontornos de Radiacion Termica (Vista en Planta)",
                 color='#f8fafc', fontsize=10, fontweight='bold', pad=8)
    ax.set_xlabel("Distancia Axial X (m)", color='#94a3b8', fontsize=8.5)
    ax.set_ylabel("Distancia Transversal Y (m)", color='#94a3b8', fontsize=8.5)

    ax.tick_params(colors='#94a3b8', labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_color('#334155')

    ax.grid(True, linestyle=':', alpha=0.4, color='#475569')
    ax.legend(loc='upper right', facecolor='#0f172a', edgecolor='#334155',
              fontsize=7, labelcolor='#f8fafc')

    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=220, bbox_inches='tight')
    plt.close(fig)
    img_buf.seek(0)
    return img_buf


def build_hyram_pdf_report(input_params: dict, results: dict, seal_data: dict) -> bytes:
    """
    Construye el documento PDF ejecutivo full-color con ReportLab.
    Retorna los bytes del archivo PDF listo para descarga.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=45
    )

    # Metadatos del documento PDF
    doc.title = f"Informe Tecnico HyRAM - {seal_data['certificate_id']}"
    doc.author = "Grupo VALIO S.A.S."
    doc.subject = "Analisis Cuantitativo de Radiacion Termica y Consecuencias"
    doc.creator = "VALIO Process Safety Suite"

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        spaceAfter=6
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=6,
        spaceAfter=4
    )

    body_text = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    legal_text = ParagraphStyle(
        'LegalClause',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#64748b'),
        alignment=4  # Justified
    )

    kpi_val_style = ParagraphStyle(
        'KpiVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        alignment=1
    )

    kpi_lbl_style = ParagraphStyle(
        'KpiLbl',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#64748b'),
        alignment=1
    )

    story = []

    # 1. ENCABEZADO CORPORATIVO
    header_data = [
        [
            Paragraph("<b>GRUPO VALIO S.A.S.</b><br/><font size=7 color='#64748b'>Consultoria & Ingenieria en Seguridad de Procesos (PPAM)</font>", body_text),
            Paragraph(f"<b>IDENTIFICADOR DE INFORME:</b> <font color='#0284c7'>{seal_data['certificate_id']}</font><br/>"
                      f"<font size=7 color='#64748b'>Fecha Emision: {seal_data['timestamp_utc']}</font>", ParagraphStyle('HdrRight', parent=body_text, alignment=2))
        ]
    ]
    t_header = Table(header_data, colWidths=[3.7 * inch, 3.7 * inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#0284c7')),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))

    # Título del Informe
    story.append(Paragraph("INFORME TECNICO DE CONSECUENCIAS Y DISTANCIAS DE SEGURIDAD", title_style))
    story.append(Paragraph(
        "Evaluacion cuantitativa de radiacion termica en chorros de fuego (Jet Fires) segun modelos fisicos de <b>HyRAM+ v6.1 (Sandia National Laboratories)</b> y normativas <b>NFPA 2 / API 521</b>.",
        subtitle_style
    ))

    # 2. CONDICIONES DE ENTRADA
    story.append(Paragraph("1. Condiciones Operacionales y Parametros del Escenario", section_heading))

    fluid_str = sanitize_formula_for_pdf(input_params.get('fluid_name', 'N/A'))

    inputs_table_data = [
        [
            Paragraph("<b>Fluido Modelado:</b>", body_text), Paragraph(fluid_str, body_text),
            Paragraph("<b>Presion Almacenamiento:</b>", body_text), Paragraph(f"{input_params.get('pressure_val', 0):.1f} {input_params.get('pressure_unit', 'bar')} ({input_params.get('pressure_pa', 0)/1e5:.1f} bar abs)", body_text)
        ],
        [
            Paragraph("<b>Temperatura Gas:</b>", body_text), Paragraph(f"{input_params.get('temp_c', 0):.1f} C ({input_params.get('temp_k', 0):.1f} K)", body_text),
            Paragraph("<b>Diametro Orificio:</b>", body_text), Paragraph(f"{input_params.get('orif_val', 0):.2f} {input_params.get('orif_unit', 'mm')} ({input_params.get('orif_m', 0)*1000:.2f} mm)", body_text)
        ],
        [
            Paragraph("<b>Coeficiente Descarga (Cd):</b>", body_text), Paragraph(f"{input_params.get('cd', 0.85):.2f}", body_text),
            Paragraph("<b>Condicion Ambiental:</b>", body_text), Paragraph(f"{input_params.get('amb_temp_c', 25):.1f} C | {input_params.get('rh', 80):.0f}% HR | {input_params.get('amb_pres_kpa', 101.325):.1f} kPa", body_text)
        ]
    ]
    t_inputs = Table(inputs_table_data, colWidths=[1.8 * inch, 1.9 * inch, 1.9 * inch, 1.8 * inch])
    t_inputs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_inputs)
    story.append(Spacer(1, 6))

    # 3. INDICADORES CLAVE (KPIS)
    story.append(Paragraph("2. Indicadores Principales de Riesgo Termico (KPIs)", section_heading))

    mass_g_s = results['mass_flow'] * 1000
    mass_kg_h = results['mass_flow'] * 3600
    flame_m = results['flame_length']
    power_kw = results['s_rad'] / 1000
    regime_str = "Sonico (Choked)" if results['choked'] else "Subsonico"

    kpis_data = [
        [
            Paragraph(f"<b>{mass_g_s:.2f} g/s</b>", kpi_val_style),
            Paragraph(f"<b>{flame_m:.2f} m</b>", kpi_val_style),
            Paragraph(f"<b>{power_kw:.1f} kW</b>", kpi_val_style),
            Paragraph(f"<b>{regime_str}</b>", kpi_val_style)
        ],
        [
            Paragraph(f"Tasa de Fuga Masica<br/><font color='#64748b'>({mass_kg_h:.1f} kg/h)</font>", kpi_lbl_style),
            Paragraph("Longitud de Llama<br/><font color='#64748b'>Visible (Ekoto et al.)</font>", kpi_lbl_style),
            Paragraph(f"Potencia Radiativa<br/><font color='#64748b'>({power_kw/1000:.3f} MW)</font>", kpi_lbl_style),
            Paragraph("Regimen de Escape<br/><font color='#64748b'>Flujo en Orificio</font>", kpi_lbl_style)
        ]
    ]
    t_kpis = Table(kpis_data, colWidths=[1.85 * inch, 1.85 * inch, 1.85 * inch, 1.85 * inch])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0284c7')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 4),
    ]))
    story.append(t_kpis)
    story.append(Spacer(1, 6))

    # 4. HUELLA 2D DE ISOCONTORNOS
    story.append(Paragraph("3. Mapa 2D de Isocontornos de Radiacion Termica", section_heading))
    img_buf = generate_footprint_image(results['distances'], results['flame_length'])
    story.append(Image(img_buf, width=7.2 * inch, height=3.0 * inch))
    story.append(Spacer(1, 6))

    # 5. MATRIZ NORMATIVA DE DISTANCIAS
    story.append(Paragraph("4. Matriz Normativa de Distancias de Separacion (NFPA 2 / API 521)", section_heading))

    d_16 = results['distances'].get(1600)
    d_47 = results['distances'].get(4700)
    d_98 = results['distances'].get(9800)
    d_25 = results['distances'].get(25000)

    matrix_rows = [
        [
            Paragraph("<b>Nivel Termico</b>", body_text),
            Paragraph("<b>Norma Referencia</b>", body_text),
            Paragraph("<b>Efecto Fisiologico / Criterio de Dano</b>", body_text),
            Paragraph("<b>Distancia Req.</b>", ParagraphStyle('HdrDist', parent=body_text, alignment=2))
        ],
        [
            Paragraph("<font color='#059669'><b>1.6 kW/m<sup>2</sup></b></font>", body_text),
            Paragraph("NFPA 2 / API 521", body_text),
            Paragraph("Limite seguro de permanencia prolongada para publico general sin EPP.", body_text),
            Paragraph(f"<b>{d_16:.2f} m</b>" if d_16 else "N/A", ParagraphStyle('ValDist', parent=body_text, alignment=2))
        ],
        [
            Paragraph("<font color='#d97706'><b>4.7 kW/m<sup>2</sup></b></font>", body_text),
            Paragraph("NFPA 2 / API 521", body_text),
            Paragraph("Limite de escape de personal calificado (dolor en ~15-20 s; sin quemaduras 2do grado).", body_text),
            Paragraph(f"<b>{d_47:.2f} m</b>" if d_47 else "N/A", ParagraphStyle('ValDist', parent=body_text, alignment=2))
        ],
        [
            Paragraph("<font color='#ea580c'><b>9.8 kW/m<sup>2</sup></b></font>", body_text),
            Paragraph("API 521 / NFPA 59A", body_text),
            Paragraph("Limite de dano a equipos e instrumentacion sin aislamiento ignifugo.", body_text),
            Paragraph(f"<b>{d_98:.2f} m</b>" if d_98 else "N/A", ParagraphStyle('ValDist', parent=body_text, alignment=2))
        ],
        [
            Paragraph("<font color='#dc2626'><b>25.0 kW/m<sup>2</sup></b></font>", body_text),
            Paragraph("API 521", body_text),
            Paragraph("Radiacion critica destructiva; ignicion de madera y dano estructural rapido.", body_text),
            Paragraph(f"<b>{d_25:.2f} m</b>" if d_25 else "N/A", ParagraphStyle('ValDist', parent=body_text, alignment=2))
        ],
    ]
    t_matrix = Table(matrix_rows, colWidths=[1.1 * inch, 1.2 * inch, 3.8 * inch, 1.3 * inch])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ecfdf5')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fffbeb')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fff7ed')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#fef2f2')),
    ]))
    story.append(t_matrix)
    story.append(Spacer(1, 8))

    # 6. MARCO LEGAL Y LICENCIAS
    legal_box = [
        [
            Paragraph(
                "<b>AVISO LEGAL Y CLAUSULA DE EXCLUSION DE RESPONSABILIDAD:</b><br/>"
                "El presente informe tecnico ha sido generado por la plataforma <i>HyRAM+ Web</i> "
                "de <b>Grupo VALIO S.A.S.</b> con propositos <b>estrictamente preliminares, pedagogicos y de evaluacion conceptual</b>. "
                "Este documento no sustituye un Analisis Cuantitativo de Riesgos (QRA) definitivo ni una memoria "
                "de calculo pericial firmada por ingenieros matriculados.<br/>"
                "<b>Exoneracion:</b> Ni Grupo VALIO S.A.S. ni sus colaboradores asumen responsabilidad "
                "legal, civil o comercial por decisiones operativas o danos derivados del uso de estos resultados.<br/>"
                "<b>Regimen de Licencia:</b> El motor fisico corresponde a <b>HyRAM+ v6.1</b>, desarrollado por "
                "<b>Sandia National Laboratories / NTESS / US DOE</b> bajo licencia <b>GNU General Public License v3.0 (GPL-3.0)</b>. "
                "Esta adaptacion web respeta dicha licencia sin implicar patrocinio de agencias gubernamentales de EE.UU.",
                legal_text
            )
        ],
        [
            Paragraph(
                f"<b>Control de Integridad:</b> Ref: {seal_data['certificate_id']} | "
                f"Emision: {seal_data['timestamp_utc']} | Grupo VALIO S.A.S. (www.grupovalio.com)",
                ParagraphStyle('HashStamp', parent=legal_text, fontSize=6.5, leading=8, textColor=colors.HexColor('#475569'))
            )
        ]
    ]
    t_legal = Table(legal_box, colWidths=[7.4 * inch])
    t_legal.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(KeepTogether(t_legal))

    # Construir documento
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
