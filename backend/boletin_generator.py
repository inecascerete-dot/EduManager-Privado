"""
Generador de boletines académicos PDF — Preescolar Casita de los Niños
Usa ReportLab Platypus para reproducir fielmente el formato institucional.
"""
from io import BytesIO
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Table, TableStyle, Paragraph, Spacer, HRFlowable, PageBreak, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics


# ── Constantes de layout ───────────────────────────────────────────────────────
PW, PH      = letter          # 612 × 792 pt
MARGIN_H    = 1.4 * cm
MARGIN_V    = 1.4 * cm
CW          = PW - 2 * MARGIN_H   # ancho del contenido ≈ 489 pt

# Proporciones de columnas de la tabla principal
COL_DIM   = 2.9 * cm     # DIMENSIÓN / ASIGNATURA
COL_IND   = CW - 2.9*cm - 2.5*cm - 2.6*cm   # INDICADORES (rest)
COL_VAL   = 2.5 * cm     # VALORACIÓN
COL_DES   = 2.6 * cm     # DESEMPEÑO

# ── Estilos de párrafo ─────────────────────────────────────────────────────────
def _estilos():
    base_font = "Helvetica"
    bold_font = "Helvetica-Bold"

    titulo_inst = ParagraphStyle(
        "titulo_inst", fontName=bold_font, fontSize=11,
        leading=14, alignment=TA_CENTER, spaceAfter=0,
    )
    eslogan = ParagraphStyle(
        "eslogan", fontName=base_font, fontSize=8,
        leading=10, alignment=TA_CENTER, spaceAfter=0,
    )
    inf_acad = ParagraphStyle(
        "inf_acad", fontName=bold_font, fontSize=9,
        leading=11, alignment=TA_CENTER, spaceAfter=0,
    )
    periodo_st = ParagraphStyle(
        "periodo_st", fontName=bold_font, fontSize=9,
        leading=11, alignment=TA_CENTER, spaceAfter=0,
    )
    est_nombre = ParagraphStyle(
        "est_nombre", fontName=bold_font, fontSize=9,
        leading=11, alignment=TA_LEFT,
    )
    est_valor = ParagraphStyle(
        "est_valor", fontName=base_font, fontSize=9,
        leading=11, alignment=TA_LEFT,
    )
    hdr_tabla = ParagraphStyle(
        "hdr_tabla", fontName=bold_font, fontSize=8,
        leading=10, alignment=TA_CENTER,
    )
    dim_cell = ParagraphStyle(
        "dim_cell", fontName=bold_font, fontSize=7.5,
        leading=9.5, alignment=TA_CENTER,
    )
    ind_cell = ParagraphStyle(
        "ind_cell", fontName=base_font, fontSize=7.5,
        leading=10, alignment=TA_LEFT,
        leftIndent=4,
    )
    val_cell = ParagraphStyle(
        "val_cell", fontName=bold_font, fontSize=8.5,
        leading=10, alignment=TA_CENTER,
    )
    des_cell = ParagraphStyle(
        "des_cell", fontName=bold_font, fontSize=8,
        leading=10, alignment=TA_CENTER,
    )
    footer_lbl = ParagraphStyle(
        "footer_lbl", fontName=bold_font, fontSize=8,
        leading=10, alignment=TA_LEFT,
    )
    footer_val = ParagraphStyle(
        "footer_val", fontName=base_font, fontSize=8,
        leading=10, alignment=TA_LEFT,
    )
    obs_lbl = ParagraphStyle(
        "obs_lbl", fontName=bold_font, fontSize=8,
        leading=10, alignment=TA_LEFT,
    )
    dir_firma = ParagraphStyle(
        "dir_firma", fontName=base_font, fontSize=8,
        leading=10, alignment=TA_LEFT,
    )
    addr_foot = ParagraphStyle(
        "addr_foot", fontName=base_font, fontSize=7,
        leading=9, alignment=TA_CENTER,
    )
    return {
        "titulo_inst": titulo_inst, "eslogan": eslogan,
        "inf_acad": inf_acad, "periodo_st": periodo_st,
        "est_nombre": est_nombre, "est_valor": est_valor,
        "hdr_tabla": hdr_tabla, "dim_cell": dim_cell,
        "ind_cell": ind_cell, "val_cell": val_cell, "des_cell": des_cell,
        "footer_lbl": footer_lbl, "footer_val": footer_val,
        "obs_lbl": obs_lbl, "dir_firma": dir_firma, "addr_foot": addr_foot,
    }


def _fmt_nota(valor):
    """Formatea nota al estilo colombiano: 4.0 → '4,00'"""
    if valor is None:
        return "—"
    return f"{valor:.2f}".replace(".", ",")


def _escala_texto(escala):
    """Genera la línea de escala de valoración dinámica."""
    partes = []
    for n in sorted(escala, key=lambda x: x.get("orden", 0)):
        mn = float(n["valor_min"])
        mx = float(n["valor_max"])
        partes.append(f"{_fmt_nota(mn)} A {_fmt_nota(mx)} {n['id_nivel']}")
    return "ESCALA DE VALORACION:   " + "     ".join(partes)


def _construir_bloque_estudiante(datos, periodo_nombre, institucion,
                                  escala_niveles, st):
    """Retorna lista de Flowables para UN estudiante."""
    story = []

    # ── ENCABEZADO ─────────────────────────────────────────────────────────────
    logo_path = os.path.join("assets", institucion.get("logo_url", ""))
    if logo_path and os.path.exists(logo_path):
        from reportlab.platypus import Image as RLImage
        logo_img = RLImage(logo_path, width=1.6*cm, height=1.6*cm)
    else:
        logo_img = Paragraph("", st["eslogan"])

    nombre_inst = (institucion.get("nombre_institucion") or "").upper()
    eslogan_txt = (institucion.get("eslogan") or institucion.get("mision") or "").upper()

    hdr_texto = Table(
        [[
            Paragraph(nombre_inst, st["titulo_inst"]),
            Paragraph(eslogan_txt, st["eslogan"]),
            Paragraph("INFORME ACADEMICO", st["inf_acad"]),
            Paragraph(periodo_nombre.upper(), st["periodo_st"]),
        ]],
        colWidths=[CW],
        rowHeights=None,
    )

    # Logo a la izquierda, texto a la derecha
    LOGO_W = 2.0 * cm
    hdr_table = Table(
        [[logo_img,
          Table(
              [[Paragraph(nombre_inst, st["titulo_inst"])],
               [Paragraph(eslogan_txt, st["eslogan"])],
               [Paragraph("INFORME ACADEMICO", st["inf_acad"])],
               [Paragraph(periodo_nombre.upper(), st["periodo_st"])]],
              colWidths=[CW - LOGO_W - 0.3*cm],
          )]],
        colWidths=[LOGO_W, CW - LOGO_W],
        rowHeights=[None],
    )
    hdr_table.setStyle(TableStyle([
        ("VALIGN",   (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",    (0, 0), (0, 0),   "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 2),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 2),
        ("BOX",      (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(hdr_table)
    story.append(Spacer(1, 0.25*cm))

    # ── DATOS DEL ESTUDIANTE ───────────────────────────────────────────────────
    nivel     = datos.get("nivel", "PRIMARIA")
    lbl_col   = "DIMENSION" if nivel == "PREESCOLAR" else "ASIGNATURA"
    est_tabla = Table(
        [[Paragraph(datos["nombre_completo"], st["est_nombre"]),
          Paragraph(f'GRADO:&nbsp;&nbsp;&nbsp;<b>{datos["nombre_grado"].upper()}</b>',
                    st["est_valor"])]],
        colWidths=[CW * 0.72, CW * 0.28],
    )
    est_tabla.setStyle(TableStyle([
        ("VALIGN",   (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
    ]))
    story.append(est_tabla)
    story.append(Spacer(1, 0.15*cm))

    # ── TABLA PRINCIPAL ────────────────────────────────────────────────────────
    # Cabecera
    t_data = [[
        Paragraph(lbl_col,      st["hdr_tabla"]),
        Paragraph("INDICADOR",  st["hdr_tabla"]),
        Paragraph("VALORACION", st["hdr_tabla"]),
        Paragraph("DESEMPEÑO",  st["hdr_tabla"]),
    ]]
    t_style = [
        # Cabecera
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#d0d0d0")),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 8),
        ("ALIGN",       (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",      (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, 0), 3),
        ("BOTTOMPADDING",(0, 0),(-1, 0), 3),
        # Grilla completa
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN",      (0, 1), (-1, -1), "MIDDLE"),
        ("ALIGN",       (2, 1), (3, -1), "CENTER"),
        ("TOPPADDING",  (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 1),(-1, -1), 4),
        ("LEFTPADDING", (0, 1), (-1, -1), 4),
        ("RIGHTPADDING",(0, 1), (-1, -1), 4),
    ]

    # Filas de asignaturas
    for row_idx, asig in enumerate(datos["asignaturas"], start=1):
        inds = asig.get("indicadores", [])
        if inds:
            ind_text = "<br/>".join(
                f"• {ind.strip()}" for ind in inds
            )
        else:
            ind_text = "<i>(Sin indicadores definidos para este período)</i>"

        nota  = asig.get("nota")
        nid   = ""
        nnom  = "—"
        for n in sorted(escala_niveles, key=lambda x: x.get("orden", 0)):
            if nota is not None and float(n["valor_min"]) <= nota <= float(n["valor_max"]):
                nid  = n["id_nivel"]
                nnom = n["id_nivel"]
                break

        t_data.append([
            Paragraph(asig["nombre"].upper(), st["dim_cell"]),
            Paragraph(ind_text, st["ind_cell"]),
            Paragraph(_fmt_nota(nota), st["val_cell"]),
            Paragraph(nnom, st["des_cell"]),
        ])

    main_table = Table(
        t_data,
        colWidths=[COL_DIM, COL_IND, COL_VAL, COL_DES],
        repeatRows=1,
    )
    main_table.setStyle(TableStyle(t_style))
    story.append(main_table)
    story.append(Spacer(1, 0.2*cm))

    # ── FILA DE TOTALES ────────────────────────────────────────────────────────
    promedio  = datos.get("promedio")
    prom_fmt  = _fmt_nota(promedio)
    prom_nivel = ""
    for n in sorted(escala_niveles, key=lambda x: x.get("orden", 0)):
        if promedio is not None and float(n["valor_min"]) <= promedio <= float(n["valor_max"]):
            prom_nivel = n["id_nivel"]
            break

    totales_t = Table(
        [[
            Paragraph(f"<b>INASISTENCIAS:</b>   {datos.get('inasistencias', 0)}", st["footer_lbl"]),
            Paragraph(f"<b>PROMEDIO:</b>   {prom_fmt}   <b>{prom_nivel}</b>", st["footer_lbl"]),
        ]],
        colWidths=[CW * 0.45, CW * 0.55],
    )
    totales_t.setStyle(TableStyle([
        ("BOX",     (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN",  (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]))
    story.append(totales_t)
    story.append(Spacer(1, 0.15*cm))

    # ── ESCALA DE VALORACIÓN ───────────────────────────────────────────────────
    story.append(Paragraph(_escala_texto(escala_niveles), st["footer_lbl"]))
    story.append(Spacer(1, 0.2*cm))

    # ── OBSERVACIONES ──────────────────────────────────────────────────────────
    obs_txt = datos.get("observaciones") or ""
    story.append(Paragraph("OBSERVACIONES:", st["obs_lbl"]))
    story.append(Spacer(1, 0.1*cm))
    # Dos líneas para observaciones (o texto si ya existe)
    if obs_txt.strip():
        story.append(Paragraph(obs_txt, st["footer_val"]))
    else:
        story.append(HRFlowable(width=CW, thickness=0.5, color=colors.black))
        story.append(Spacer(1, 0.35*cm))
        story.append(HRFlowable(width=CW, thickness=0.5, color=colors.black))
    story.append(Spacer(1, 0.4*cm))

    # ── FIRMA DIRECTOR DE GRUPO ────────────────────────────────────────────────
    director = datos.get("director") or ""
    firma_t = Table(
        [[Paragraph(f"Director de grupo: {director}", st["dir_firma"]), ""]],
        colWidths=[CW * 0.55, CW * 0.45],
    )
    firma_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LINEABOVE", (0, 0), (0, 0), 0.5, colors.black),
    ]))
    story.append(firma_t)
    story.append(Spacer(1, 0.25*cm))

    # ── PIE DE PÁGINA INSTITUCIONAL ────────────────────────────────────────────
    dir_txt  = institucion.get("direccion_principal") or ""
    tel_txt  = institucion.get("telefono_principal") or ""
    mail_txt = institucion.get("email_institucional") or ""
    mun_txt  = f"{institucion.get('municipio', '')} - {institucion.get('departamento', '')}".strip(" -")
    linea1   = "  |  ".join(p for p in [dir_txt, f"Tel {tel_txt}" if tel_txt else "", mail_txt] if p)
    story.append(HRFlowable(width=CW, thickness=0.5, color=colors.black))
    story.append(Paragraph(linea1, st["addr_foot"]))
    if mun_txt:
        story.append(Paragraph(mun_txt, st["addr_foot"]))

    return story


def generar_boletin_pdf(
    lista_datos,      # list[dict] — uno por estudiante (salida de web_datos_para_boletin)
    periodo_nombre,   # str  ej. "PRIMER PERÍODO 2026"
    institucion,      # dict de instituciones
    escala_niveles,   # list[dict] de escala_valoracion
):
    """
    Genera el PDF con un boletín por página.
    Retorna BytesIO con el PDF.
    """
    buf = BytesIO()
    st  = _estilos()

    # DocTemplate con márgenes ajustados
    doc = BaseDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V,  bottomMargin=MARGIN_V,
    )
    frame = Frame(
        MARGIN_H, MARGIN_V,
        PW - 2*MARGIN_H, PH - 2*MARGIN_V,
        id="main", showBoundary=0,
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=frame)])

    story = []
    for idx, datos in enumerate(lista_datos):
        if not datos:
            continue
        if idx > 0:
            story.append(PageBreak())
        bloque = _construir_bloque_estudiante(
            datos, periodo_nombre, institucion, escala_niveles, st
        )
        story.extend(bloque)

    doc.build(story)
    buf.seek(0)
    return buf
