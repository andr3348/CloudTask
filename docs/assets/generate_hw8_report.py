#!/usr/bin/env python3
"""Genera docs/Informe-CloudTask-HW8.docx a partir de los resultados reales de infra/nlp/out/."""
import json
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parents[2]
OUT_DOCX = ROOT / "docs" / "Informe-CloudTask-HW8.docx"
DIAG_PNG = ROOT / "docs" / "assets" / "hw8-architecture.png"
TA_JSON = ROOT / "infra" / "nlp" / "out" / "text_analytics_results.json"
EVAL_JSON = ROOT / "infra" / "nlp" / "out" / "clu_eval_summary.json"
HOLD_JSON = ROOT / "infra" / "nlp" / "out" / "clu_holdout_results.json"

AZURE_BLUE = RGBColor(0x00, 0x78, 0xD4)
DARK_TEXT = RGBColor(0x32, 0x31, 0x30)
MUTED = RGBColor(0x60, 0x5E, 0x5C)


def set_cell_shading(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def add_heading(doc, text: str, level: int = 1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.name = "Calibri"
        r.font.color.rgb = AZURE_BLUE if level == 1 else DARK_TEXT
        r.font.bold = True
        r.font.size = Pt(14 if level == 1 else 11.5)
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(4)
    return p


def add_para(doc, text: str, bold_prefix: str = "", italic: bool = False, size: float = 10.5,
             color: RGBColor = DARK_TEXT, align=None, space_after: float = 5):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Calibri"
        rb.font.size = Pt(size)
        rb.font.color.rgb = color
    r = p.add_run(text)
    r.italic = italic
    r.font.name = "Calibri"
    r.font.size = Pt(size)
    r.font.color.rgb = color
    return p


def add_bullet(doc, bold_prefix: str, text: str):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Calibri"
        rb.font.size = Pt(10.5)
        rb.font.color.rgb = DARK_TEXT
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = DARK_TEXT
    return p


def add_code_block(doc, code: str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, "F3F2F1")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(code.strip())
    r.font.name = "Consolas"
    r.font.size = Pt(8.8)
    r.font.color.rgb = DARK_TEXT
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_styled_table(doc, headers: list[str], rows: list[list[str]], col_widths=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = tbl.rows[0].cells
    for idx, h in enumerate(headers):
        set_cell_shading(hdr_cells[idx], "0078D4")
        set_cell_margins(hdr_cells[idx], top=75, bottom=75, left=100, right=100)
        p = hdr_cells[idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for r_idx, row in enumerate(rows):
        cells = tbl.rows[r_idx + 1].cells
        bg = "F8FBFE" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            set_cell_shading(cells[c_idx], bg)
            set_cell_margins(cells[c_idx], top=65, bottom=65, left=100, right=100)
            p = cells[c_idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(val))
            r.font.name = "Calibri"
            r.font.size = Pt(9.2)
            r.font.color.rgb = DARK_TEXT
    if col_widths:
        for row in tbl.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)
    return tbl


def add_screenshot_box(doc, num: int, title: str, hint: str):
    add_para(doc, f" {title}", bold_prefix=f"[Captura {num}]", size=10.2, space_after=3)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, "FAF9F8")
    set_cell_margins(cell, top=220, bottom=220, left=160, right=160)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(f"Espacio reservado — pegar captura de pantalla aquí.\nRuta sugerida: {hint}")
    r.italic = True
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)
    r.font.color.rgb = MUTED
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def build_report():
    ta = json.loads(TA_JSON.read_text(encoding="utf-8"))
    ev = json.loads(EVAL_JSON.read_text(encoding="utf-8"))
    hold = json.loads(HOLD_JSON.read_text(encoding="utf-8"))

    doc = docx.Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11.0)
    sec.left_margin = Inches(1.0)
    sec.right_margin = Inches(1.0)
    sec.top_margin = Inches(0.9)
    sec.bottom_margin = Inches(0.9)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    # --- Portada ---
    for _ in range(4):
        doc.add_paragraph()

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rt = p_title.add_run("Trabajo Práctico 8: Procesamiento de Lenguaje Natural y LUIS (CLU) en Azure")
    rt.bold = True
    rt.font.name = "Calibri"
    rt.font.size = Pt(20)
    rt.font.color.rgb = AZURE_BLUE

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs = p_sub.add_run("Text Analytics y comprensión conversacional para atención de restaurante")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.font.color.rgb = MUTED

    for _ in range(3):
        doc.add_paragraph()

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rm = p_meta.add_run(
        "Carrera: Ingeniería de Software\n"
        "Asignatura: Tecnología Cloud con AWS\n"
        "Modalidad: Individual\n\n"
        "Integrante: DIEGO ANDREE VALENCIA VASQUEZ\n"
        "Fecha: Noviembre 2026\n\n"
        "Repositorio: CloudTask (infra/nlp)"
    )
    rm.font.name = "Calibri"
    rm.font.size = Pt(12)
    rm.font.color.rgb = DARK_TEXT

    doc.add_page_break()

    # --- 1. Objetivo y fundamentos ---
    add_heading(doc, "1. Objetivo y conocimientos tecnológicos", level=1)
    add_para(
        doc,
        "Comprender los aspectos básicos de la inteligencia artificial en Microsoft Azure aplicados al "
        "Procesamiento de Lenguaje Natural (PLN / NLP) mediante el despliegue y consumo de Azure AI Language "
        "(Text Analytics) y la creación, entrenamiento, despliegue y exportación de una aplicación de comprensión "
        "de lenguaje orientada a un restaurante."
    )
    add_para(
        doc,
        "El servicio clásico Language Understanding (LUIS) fue retirado oficialmente por Microsoft el 31 de marzo "
        "de 2026 y consolidado dentro de Azure AI Language como Conversational Language Understanding (CLU). "
        "En la suscripción estudiantil (Azure for Students), la consulta de SKUs confirma que LUIS/LUIS.Authoring "
        "ya no están disponibles en las regiones permitidas, mientras que el recurso unificado TextAnalytics (nivel F0) "
        "habilita tanto Text Analytics como CLU en South Central US.",
        bold_prefix="Nota de plataforma (LUIS → CLU): ",
    )

    # --- 2. Diagrama ---
    add_heading(doc, "2. Diagrama de arquitectura", level=1)
    if DIAG_PNG.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(DIAG_PNG), width=Inches(6.3))
    add_para(
        doc,
        "Figura 1. Arquitectura de la solución en Azure AI Language (Text Analytics + CLU) sobre South Central US.",
        italic=True, size=9.0, color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    # --- 3. Servicios y componentes ---
    add_heading(doc, "3. Servicios y componentes", level=1)
    add_styled_table(
        doc,
        ["Componente", "Recurso / Artefacto", "Propósito"],
        [
            ["Grupo de recursos", "rg-cloudtask-hw8 (South Central US)", "Contenedor lógico y control de costos"],
            ["Azure AI Language", "lang-hw8-4632 (TextAnalytics · F0)", "Endpoint único para Text Analytics y CLU"],
            ["Text Analytics", "POST /language/:analyze-text", "Idioma, sentimiento (opinion mining), NER y palabras clave"],
            ["Proyecto CLU", "hw8-restaurante-luis (es)", "6 intenciones, 5 entidades, 64 frases de entrenamiento"],
            ["Modelo y despliegue", "Modelo v1 (advanced) → production", "Clasificación en tiempo real (:analyze-conversations)"],
            ["Modelo exportado", "hw8-restaurante-luis-export.json", "Archivo JSON portable exportado desde Azure (21,370 bytes)"],
        ],
        col_widths=[1.6, 2.4, 2.5],
    )

    # --- 4. Procedimiento ---
    add_heading(doc, "4. Procedimiento realizado", level=1)
    add_bullet(doc, "1. Autenticación y validación regional: ",
               "Inicio de sesión en Azure CLI con la cuenta institucional 1626065@senati.pe (Azure for Students) y "
               "verificación de la política sys.regionrestriction (región elegida: southcentralus).")
    add_bullet(doc, "2. Provisión del recurso: ",
               "Creación del grupo rg-cloudtask-hw8 y del recurso lang-hw8-4632 (kind=TextAnalytics, sku=F0, dominio "
               "personalizado lang-hw8-4632).")
    add_bullet(doc, "3. Pruebas de Text Analytics: ",
               "Envío de 6 documentos (4 en español, 1 en inglés, 1 en portugués) a :analyze-text para detección de "
               "idioma, análisis de sentimiento con minería de opiniones, reconocimiento de entidades (NER) y extracción "
               "de palabras clave.")
    add_bullet(doc, "4. Diseño del modelo de restaurante (CLU): ",
               "Generación y validación UTF-16 de 64 frases en español distribuidas en 6 intenciones (RealizarPedido, "
               "ConsultarMenu, ReservarMesa, ConsultarHorarioUbicacion, CancelarPedido, None) y 5 entidades "
               "(Plato, Cantidad, TipoServicio, NumPersonas, FechaHora).")
    add_bullet(doc, "5. Importación, entrenamiento y despliegue: ",
               "Importación del proyecto vía API 2023-04-01, entrenamiento del modelo v1 con trainingMode='advanced' "
               "(requerido para español) y división automática 80/20, y publicación en el despliegue production.")
    add_bullet(doc, "6. Evaluación hold-out y exportación: ",
               "Evaluación de 18 frases independientes nunca vistas (incluidos los ejemplos de la guía) y exportación "
               "asíncrona del proyecto mediante :export hacia infra/nlp/out/hw8-restaurante-luis-export.json.")

    add_code_block(doc, """az group create --name rg-cloudtask-hw8 --location southcentralus --tags project=cloudtask-hw8
az cognitiveservices account create --name lang-hw8-4632 --resource-group rg-cloudtask-hw8 \\
  --kind TextAnalytics --sku F0 --location southcentralus --custom-domain lang-hw8-4632 --yes
python3 infra/nlp/prepare_data.py
uv run --with requests python infra/nlp/run_nlp_lab.py""")

    # --- 5. Capturas de pantalla ---
    add_heading(doc, "5. Evidencia de la implementación (capturas)", level=1)
    add_para(
        doc,
        "Portales utilizados: Azure Portal (https://portal.azure.com) y Language Studio "
        "(https://language.cognitive.azure.com) con la cuenta 1626065@senati.pe.",
        italic=True, size=9.5, color=MUTED,
    )
    captures = [
        ("Grupo de recursos rg-cloudtask-hw8 con el recurso lang-hw8-4632.",
         "Azure Portal > Grupos de recursos > rg-cloudtask-hw8"),
        ("Claves y punto de conexión del recurso lang-hw8-4632 (ocultar claves).",
         "Azure Portal > lang-hw8-4632 > Claves y punto de conexión"),
        ("Text Analytics en Language Studio (sentimiento, entidades y palabras clave).",
         "Language Studio > Classify text / Extract information > Analyze sentiment and mine opinions"),
        ("Proyecto hw8-restaurante-luis: esquema de intenciones y entidades.",
         "Language Studio > hw8-restaurante-luis > Schema definition"),
        ("Etiquetado de frases de entrenamiento (Data labeling).",
         "Language Studio > hw8-restaurante-luis > Data labeling"),
        ("Métricas de rendimiento del modelo v1 entrenado.",
         "Language Studio > hw8-restaurante-luis > Model performance"),
        ("Despliegue production y prueba interactiva ('Quiero pedir una pizza' / '¿Cuál es el menú de hoy?').",
         "Language Studio > hw8-restaurante-luis > Testing deployments"),
        ("Exportación del modelo y archivo JSON local generado.",
         "Language Studio > hw8-restaurante-luis > Export (y vista de infra/nlp/out/hw8-restaurante-luis-export.json)"),
    ]
    for i, (t, h) in enumerate(captures, 1):
        add_screenshot_box(doc, i, t, h)

    # --- 6. Resultados ---
    add_heading(doc, "6. Resultados obtenidos", level=1)

    add_heading(doc, "6.1 Text Analytics (Procesamiento de lenguaje natural)", level=2)
    lang_rows = []
    for d in ta["language_detection"]:
        dl = d["detectedLanguage"]
        lang_rows.append([d["id"], dl["name"], dl["iso6391Name"], f"{dl['confidenceScore']:.2f}"])
    add_styled_table(doc, ["Doc ID", "Idioma detectado", "Código ISO", "Confianza"], lang_rows, [0.9, 2.2, 1.5, 1.5])

    sent_map = {d["id"]: d for d in ta["sentiment_analysis"]}
    ner_map = {d["id"]: d for d in ta["entity_recognition"]}
    kp_map = {d["id"]: d for d in ta["key_phrase_extraction"]}
    nlp_rows = []
    for doc_id in ("1", "2", "3", "4"):
        s = sent_map[doc_id]
        sc = s["confidenceScores"]
        ents = ", ".join(f"{e['text']} ({e['category']})" for e in ner_map[doc_id]["entities"][:5])
        kps = ", ".join(kp_map[doc_id]["keyPhrases"][:5])
        nlp_rows.append([
            doc_id,
            f"{s['sentiment']} ({sc['positive']:.2f}/{sc['neutral']:.2f}/{sc['negative']:.2f})",
            ents,
            kps,
        ])
    add_styled_table(
        doc,
        ["Doc", "Sentimiento (pos/neu/neg)", "Entidades NER (muestra)", "Palabras clave (muestra)"],
        nlp_rows,
        col_widths=[0.5, 1.6, 2.3, 2.1],
    )

    add_heading(doc, "6.2 Evaluación interna CLU (split 80 % / 20 %)", level=2)
    ie = ev["intentsEvaluation"]
    ee = ev["entitiesEvaluation"]
    add_styled_table(
        doc,
        ["Dimensión", "Micro Precision", "Micro Recall", "Micro F1", "Macro F1"],
        [
            ["Intenciones (6 clases)", f"{ie['microPrecision']:.4f}", f"{ie['microRecall']:.4f}",
             f"{ie['microF1']:.4f}", f"{ie['macroF1']:.4f}"],
            ["Entidades (5 tipos)", f"{ee['microPrecision']:.4f}", f"{ee['microRecall']:.4f}",
             f"{ee['microF1']:.4f}", f"{ee['macroF1']:.4f}"],
        ],
        col_widths=[1.8, 1.2, 1.1, 1.1, 1.1],
    )

    add_heading(doc, "6.3 Evaluación hold-out y simulación de chatbot (18 frases)", level=2)
    add_para(
        doc,
        f"Exactitud global sobre el conjunto hold-out independiente: "
        f"{hold['holdout_correct']}/{hold['holdout_total']} = {hold['holdout_accuracy']*100:.1f} %.",
        bold_prefix="Resultado hold-out: ",
    )
    hold_rows = []
    for r in hold["holdout_predictions"]:
        ents = ", ".join(f"{e['category']}: {e['text']}" for e in r["entities"]) or "—"
        hold_rows.append([
            r["text"],
            f"{r['pred_intent']} ({r['confidence']:.4f})",
            ents,
            r["bot_reply"],
        ])
    add_styled_table(
        doc,
        ["Frase de prueba", "Intención (confianza)", "Entidades extraídas", "Respuesta simulada"],
        hold_rows,
        col_widths=[1.9, 1.5, 1.4, 1.7],
    )

    # --- 7. Costos ---
    add_heading(doc, "7. Costos y limpieza", level=1)
    add_styled_table(
        doc,
        ["Recurso", "Nivel", "Consumo", "Costo"],
        [
            ["Azure AI Language (lang-hw8-4632)", "F0 (Free)", "6 docs Text Analytics + CLU (64 train, 18 test, export)", "$0.00"],
            ["Grupo de recursos (rg-cloudtask-hw8)", "—", "Contenedor lógico", "$0.00"],
            ["Total", "", "", "$0.00"],
        ],
        col_widths=[2.3, 1.0, 2.3, 0.9],
    )
    add_para(doc, "Limpieza posterior a las capturas: az group delete --name rg-cloudtask-hw8 --yes --no-wait.")

    # --- 8. Conclusiones y dificultades ---
    add_heading(doc, "8. Conclusiones, dificultades y mejoras", level=1)
    add_bullet(doc, "Unificación en Azure AI Language: ",
               "Un solo recurso TextAnalytics F0 permitió ejecutar detección de idioma (100 % en es/en/pt), "
               "análisis de sentimiento con opinion mining, NER, extracción de palabras clave y el modelo conversacional CLU.")
    add_bullet(doc, "Desempeño del asistente de restaurante: ",
               "El modelo alcanzó 100 % de exactitud en las 18 frases hold-out, respondiendo con confianza >= 0.9998 a los "
               "casos solicitados ('Quiero pedir una pizza' → RealizarPedido; '¿Cuál es el menú de hoy?' → ConsultarMenu).")
    add_bullet(doc, "Dificultades superadas: ",
               "(1) Retiro de LUIS clásico y ausencia de SKUs LUIS en regiones permitidas; (2) ajuste del cuerpo REST "
               "2023-04-01 (modelLabel y trainingSplitPercentage); (3) uso obligatorio de trainingMode='advanced' para español.")
    add_bullet(doc, "Mejoras futuras: ",
               "Ampliar ejemplos de la clase None con nombres propios/lugares para evitar falsos positivos de entidad "
               "(como 'la Mancha' → Plato) y refinar la delimitación de unidades genéricas ('platos' vs 'ceviche').")

    # --- 9. Entregables ---
    add_heading(doc, "9. Entregables", level=1)
    add_bullet(doc, "Documento de procedimiento e informe: ", "docs/Informe-CloudTask-HW8.docx y docs/Informe-CloudTask-HW8.pdf.")
    add_bullet(doc, "Archivo exportado del modelo: ", "infra/nlp/out/hw8-restaurante-luis-export.json (21,370 bytes).")
    add_bullet(doc, "Código y documentación reproducible: ",
               "infra/nlp/prepare_data.py, infra/nlp/run_nlp_lab.py y docs/*-hw8.md en el repositorio CloudTask.")

    doc.save(OUT_DOCX)
    print(f"Informe generado en {OUT_DOCX}")


if __name__ == "__main__":
    build_report()
