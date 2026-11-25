#!/usr/bin/env python3
"""Genera la presentación HW7 (tema oscuro) usando las capturas del informe."""
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

BASE = Path("/home/andree/projects/college/cloud-task")
IMG = BASE / "docs/assets/hw7-slides"
OUT = BASE / "docs/Presentacion-HW7.pptx"

# ---------- palette ----------
BG      = RGBColor(0x0A, 0x12, 0x1F)
BG2     = RGBColor(0x10, 0x22, 0x38)
PANEL   = RGBColor(0x13, 0x22, 0x36)
PANEL2  = RGBColor(0x1A, 0x2C, 0x45)
BORDER  = RGBColor(0x2B, 0x40, 0x5C)
TEXT    = RGBColor(0xE9, 0xEF, 0xF8)
MUTED   = RGBColor(0x9C, 0xAE, 0xC6)
CYAN    = RGBColor(0x38, 0xBD, 0xF8)
GREEN   = RGBColor(0x34, 0xD3, 0x99)
AMBER   = RGBColor(0xFB, 0xBF, 0x24)
RED     = RGBColor(0xF8, 0x71, 0x71)
VIOLET  = RGBColor(0xA7, 0x8B, 0xFA)

FONT = "Segoe UI"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def rect(slide, x, y, w, h, fill, line=None, lw=1.0, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
         radius=0.06):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    return sh


def text(slide, s, x, y, w, h, size=14, color=TEXT, bold=False, italic=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0, font=FONT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = s.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    return tb


def bullets(slide, items, x, y, w, h, size=13, color=TEXT, accent=CYAN, gap=7):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.08
        rb = p.add_run()
        rb.text = "•  "
        rb.font.name = FONT
        rb.font.size = Pt(size)
        rb.font.bold = True
        rb.font.color.rgb = accent
        rt = p.add_run()
        rt.text = item
        rt.font.name = FONT
        rt.font.size = Pt(size)
        rt.font.color.rgb = color


def bg(slide, gradient=False):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    sh.line.fill.background()
    sh.shadow.inherit = False
    if gradient:
        sh.fill.gradient()
        sh.fill.gradient_angle = 45
        stops = sh.fill.gradient_stops
        stops[0].color.rgb = BG
        stops[0].position = 0.0
        stops[1].color.rgb = BG2
        stops[1].position = 1.0
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = BG


def header(slide, kicker, title, subtitle=None):
    text(slide, kicker.upper(), 0.6, 0.30, 12.1, 0.28, 10.5, CYAN, bold=True)
    text(slide, title, 0.6, 0.57, 12.1, 0.75, 27, TEXT, bold=True)
    rect(slide, 0.6, 1.36, 1.15, 0.055, CYAN, shape=MSO_SHAPE.RECTANGLE)
    if subtitle:
        text(slide, subtitle, 0.6, 1.46, 12.1, 0.3, 11.5, MUTED)


def footer(slide, n):
    text(slide, "TP07 · Azure Custom Vision · SENATI", 0.6, 7.16, 8.5, 0.22, 8.5, MUTED)
    text(slide, f"{n:02d}", 12.2, 7.14, 0.55, 0.22, 9, MUTED, align=PP_ALIGN.RIGHT)


def image(slide, path, x, y, w, h, border=True, pad=0.05):
    im = Image.open(path)
    iw, ih = im.size
    scale = min(w / iw, h / ih)
    nw, nh = iw * scale, ih * scale
    px, py = x + (w - nw) / 2, y + (h - nh) / 2
    if border:
        rect(slide, px - pad, py - pad, nw + 2 * pad, nh + 2 * pad, PANEL, BORDER, 0.9,
             shape=MSO_SHAPE.RECTANGLE)
    slide.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(nw), Inches(nh))
    return px, py, nw, nh


def caption(slide, s, x, y, w, align=PP_ALIGN.CENTER):
    text(slide, s, x, y, w, 0.28, 9.5, MUTED, italic=True, align=align)


def stat(slide, x, y, w, h, value, label, accent):
    rect(slide, x, y, w, h, PANEL, BORDER, 0.9)
    text(slide, value, x + 0.18, y + 0.12, w - 0.36, h * 0.55, 26, accent, bold=True)
    text(slide, label, x + 0.18, y + h * 0.62, w - 0.36, h * 0.32, 9.5, MUTED)


def pill(slide, s, x, y, w, color=CYAN):
    rect(slide, x, y, w, 0.34, PANEL2, BORDER, 0.8)
    text(slide, s, x, y + 0.055, w, 0.24, 9.5, color, bold=True, align=PP_ALIGN.CENTER)


# =====================================================================
# 1. PORTADA
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s, gradient=True)
text(s, "TRABAJO PRÁCTICO 07  ·  COMPUTER VISION", 0.85, 1.25, 8.6, 0.3, 11, CYAN, bold=True)
text(s, "Computer Vision\nen Azure", 0.85, 1.65, 8.6, 1.65, 46, TEXT, bold=True, spacing=0.95)
text(s, "Clasificación gatos vs. perros con Custom Vision: sin código, con pruebas reales.",
     0.85, 3.55, 7.9, 0.9, 17, MUTED, spacing=1.15)
rect(s, 0.85, 4.72, 2.2, 0.055, CYAN, shape=MSO_SHAPE.RECTANGLE)
text(s, "SENATI  ·  Tecnología Cloud", 0.85, 5.0, 7.0, 0.3, 12, TEXT, bold=True)
text(s, "[Nombre Apellido]  ·  Noviembre 2026", 0.85, 5.32, 7.0, 0.3, 11.5, MUTED)
text(s, "github.com/andr3348/CloudTask", 0.85, 6.55, 7.0, 0.3, 10.5, CYAN)
text(s, "07", 9.15, 1.1, 3.6, 3.0, 190, RGBColor(0x16, 0x2D, 0x48), bold=True, align=PP_ALIGN.CENTER)
text(s, "AZURE  ·  F0  ·  ONNX", 9.2, 5.05, 3.4, 0.3, 10, MUTED, bold=True, align=PP_ALIGN.CENTER)

# =====================================================================
# 2. DESCRIPCIÓN
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "El trabajo", "Enseñar a una máquina a distinguir gatos y perros",
       "Custom Vision: transfer learning sin escribir código")
text(s, "El trabajo implementa un clasificador de imágenes con Azure Custom Vision: se crean los "
        "recursos Training y Prediction en nivel F0, se prepara y etiqueta un dataset, se entrena "
        "con quick training, se publica el modelo y se prueba con imágenes que nunca vio.",
     0.6, 1.92, 7.25, 1.15, 13, TEXT, spacing=1.15)
text(s, "Todo el flujo se automatizó con Azure CLI y la API REST v3.4-preview. El resultado se "
        "exportó a ONNX para poder ejecutarlo fuera de Azure.",
     0.6, 3.15, 7.25, 0.8, 13, MUTED, spacing=1.15)
pill(s, "Sin código", 0.6, 4.18, 1.55, GREEN)
pill(s, "General (compact)", 2.3, 4.18, 2.15, CYAN)
pill(s, "Multiclase · 2 tags", 4.6, 4.18, 2.35, VIOLET)

stat(s, 8.3, 1.9, 2.15, 1.15, "60", "imágenes de entrenamiento", CYAN)
stat(s, 10.65, 1.9, 2.15, 1.15, "20", "imágenes hold-out", VIOLET)
stat(s, 8.3, 3.2, 2.15, 1.15, "85%", "exactitud real", GREEN)
stat(s, 10.65, 3.2, 2.15, 1.15, "$0", "costo · nivel F0", AMBER)

rect(s, 0.6, 5.15, 12.15, 1.25, PANEL, BORDER, 0.9)
text(s, "PIPELINE", 0.9, 5.28, 3.0, 0.25, 9, CYAN, bold=True)
text(s, "Dataset  →  Training  →  Proyecto  →  Iteración  →  Prediction  →  ONNX",
     0.9, 5.62, 11.6, 0.45, 15, TEXT, bold=True, align=PP_ALIGN.CENTER)
footer(s, 2)

# =====================================================================
# 3. ARQUITECTURA (diagrama del informe, a sangre)
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
image(s, IMG / "diagram.png", 0.45, 0.35, 12.43, 6.55, pad=0.04)
text(s, "Figura 1 · Arquitectura implementada: Training y Prediction en F0, proyecto multiclase, "
        "iteración publicada y exportación ONNX.", 0.75, 7.02, 11.9, 0.3, 9.5, MUTED, italic=True,
     align=PP_ALIGN.CENTER)

# =====================================================================
# 4. IMPLEMENTACIÓN (recursos)
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "Implementación", "Recursos creados en Azure (nivel gratuito F0)",
       "Suscripción Azure for Students · región South Central US")
image(s, IMG / "captura1.png", 0.55, 1.75, 8.0, 2.55)
caption(s, "Grupo de recursos con los dos recursos Custom Vision.", 0.55, 4.38, 8.0, PP_ALIGN.LEFT)
image(s, IMG / "captura2.png", 8.8, 1.75, 4.0, 2.55)
caption(s, "Training: claves y endpoint (claves ocultas).", 8.8, 4.38, 4.0, PP_ALIGN.LEFT)

cards = [
    ("Training · F0", "cv-hw7-train-4632", "60 imágenes · 2 etiquetas\n1 iteración entrenada", CYAN),
    ("Prediction · F0", "cv-hw7-pred-4632", "Endpoint REST publicado\ncomo hw7-iter1", GREEN),
    ("Región", "South Central US", "Permitida por la política de\nla suscripción estudiantil", AMBER),
]
for i, (title, sub, body, color) in enumerate(cards):
    x = 0.55 + i * 4.12
    rect(s, x, 4.9, 3.9, 1.75, PANEL, BORDER, 0.9)
    rect(s, x, 4.9, 0.06, 1.75, color, shape=MSO_SHAPE.RECTANGLE)
    text(s, title, x + 0.22, 5.02, 3.5, 0.28, 12.5, color, bold=True)
    text(s, sub, x + 0.22, 5.34, 3.5, 0.26, 10.5, TEXT, bold=True)
    text(s, body, x + 0.22, 5.65, 3.5, 0.8, 9.5, MUTED, spacing=1.10)
footer(s, 4)

# =====================================================================
# 5. PROYECTO Y DATASET
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "Datos", "Proyecto y dataset: 60 imágenes etiquetadas",
       "30 gatos + 30 perros para entrenar · 20 imágenes reservadas para probar")
image(s, IMG / "captura3.png", 0.55, 1.8, 3.7, 4.85)
caption(s, "Settings: General (compact), Multiclass, 2 tags.", 0.55, 6.72, 3.7, PP_ALIGN.LEFT)
image(s, IMG / "captura4.png", 4.55, 1.8, 8.2, 4.85)
caption(s, "Training Images: 30 cats + 30 dogs etiquetados.", 4.55, 6.72, 8.2, PP_ALIGN.LEFT)
footer(s, 5)

# =====================================================================
# 6. VALIDACIÓN INTERNA
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "Pruebas · 1", "Validación interna: 100% en precision, recall y AP",
       "Captura del portal · iteración hw7-iter1 · umbral 50%")
image(s, IMG / "captura5.png", 0.55, 1.8, 7.6, 4.95)
caption(s, "Performance del portal para la iteración publicada.", 0.55, 6.82, 7.6, PP_ALIGN.LEFT)
for i, (v, l, c) in enumerate([("100%", "Precision", VIOLET), ("100%", "Recall", CYAN), ("100%", "Average Precision", GREEN)]):
    y = 1.85 + i * 1.05
    rect(s, 8.45, y, 4.25, 0.9, PANEL, BORDER, 0.9)
    rect(s, 8.45, y, 0.06, 0.9, c, shape=MSO_SHAPE.RECTANGLE)
    text(s, v, 8.68, y + 0.12, 1.3, 0.55, 24, c, bold=True)
    text(s, l, 10.0, y + 0.29, 2.55, 0.3, 11.5, TEXT, bold=True)
rect(s, 8.45, 5.15, 4.25, 1.5, RGBColor(0x2B, 0x22, 0x10), RGBColor(0x6B, 0x52, 0x1E), 1.0)
text(s, "Lectura crítica", 8.68, 5.26, 3.8, 0.25, 10, AMBER, bold=True)
text(s, "Es la métrica interna del servicio sobre su propio split de validación: puede ser "
        "optimista. La prueba con datos nuevos es la que manda.", 8.68, 5.56, 3.8, 0.95, 9.8, TEXT, spacing=1.1)
footer(s, 6)

# =====================================================================
# 7. HOLD-OUT
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "Pruebas · 2", "Prueba real: 85% de exactitud con imágenes nuevas",
       "20 imágenes hold-out nunca usadas en entrenamiento (10 gatos / 10 perros)")
image(s, IMG / "captura6.png", 0.55, 1.85, 7.35, 4.75)
caption(s, "Quick Test con una imagen no vista: cats 99,9%.", 0.55, 6.68, 7.35, PP_ALIGN.LEFT)
text(s, "85%", 8.2, 1.55, 4.4, 0.95, 54, GREEN, bold=True)
text(s, "17 de 20 imágenes clasificadas correctamente", 8.25, 2.45, 4.4, 0.28, 11, MUTED)

# matriz de confusión dibujada
cx, cy, cw, ch = 8.2, 3.15, 1.5, 0.5
text(s, "", cx, cy - 0.3, cw, 0.25, 9, MUTED)
text(s, "pred cats", cx + cw, cy - 0.3, cw, 0.25, 9, MUTED, align=PP_ALIGN.CENTER)
text(s, "pred dogs", cx + 2 * cw, cy - 0.3, cw, 0.25, 9, MUTED, align=PP_ALIGN.CENTER)
rows = [("real cats", "7", "3"), ("real dogs", "0", "10")]
for r, (lab, a, b) in enumerate(rows):
    y = cy + r * (ch + 0.06)
    text(s, lab, cx, y + 0.1, cw, 0.3, 9.5, MUTED)
    for c, val in enumerate([a, b]):
        good = (r == 0 and c == 0) or (r == 1 and c == 1)
        col = GREEN if good else (RED if val != "0" else MUTED)
        fill = RGBColor(0x10, 0x3A, 0x2C) if good else (RGBColor(0x3A, 0x16, 0x1E) if val != "0" else PANEL)
        rect(s, cx + (c + 1) * cw, y, cw - 0.04, ch, fill, BORDER, 0.6, radius=0.08)
        text(s, val, cx + (c + 1) * cw, y + 0.10, cw - 0.04, 0.3, 13, col, bold=True, align=PP_ALIGN.CENTER)
text(s, "Matriz de confusión · hold-out", cx, cy + 2 * (ch + 0.06) + 0.04, 4.4, 0.25, 9, MUTED, italic=True)
bullets(s, ["cats: 7/10 correctos (recall 0,70)", "dogs: 10/10 correctos (recall 1,00)",
            "3 gatos predichos como perro (0,64–0,80)"],
        8.25, 4.95, 4.45, 1.05, 11.5, TEXT, RED, gap=4)
rect(s, 8.25, 6.02, 4.45, 0.62, RGBColor(0x2B, 0x22, 0x10), RGBColor(0x6B, 0x52, 0x1E), 1.0)
text(s, "La métrica interna (100%) no se sostiene con datos nuevos.", 8.42, 6.17, 4.15, 0.3, 10, AMBER, bold=True)
footer(s, 7)

# =====================================================================
# 8. ERRORES
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "Pruebas · 3", "Dónde falla el modelo: gatos atípicos y fondos",
       "Predictions sobre imágenes de prueba: el error también es evidencia")
px, py, nw, nh = image(s, IMG / "captura8_errors.png", 0.55, 1.8, 12.23, 4.9)
# resaltar el gato clasificado como perro (68,5%)
rx = px + 0.283 * nw
ry = py + 0.185 * nh
hl = rect(s, rx, ry, 0.129 * nw, 0.365 * nh, PANEL, RED, 2.2, radius=0.03)
hl.fill.background()
pill(s, "gato → perro · 68,5%", rx + 0.14 * nw, ry - 0.12, 2.55, RED)
caption(s, "3 de 20 errores del hold-out fueron gatos; el modelo confunde poses y fondos poco frecuentes.",
        0.55, 6.76, 12.2, PP_ALIGN.LEFT)
footer(s, 8)

# =====================================================================
# 9. EXPORTACIÓN
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "Entregable", "Modelo exportado a ONNX, listo para el borde",
       "La iteración queda publicada y el modelo se descarga como ZIP")
image(s, IMG / "captura7.png", 0.55, 1.8, 7.9, 4.7)
caption(s, "Export → ONNX → Download desde el portal.", 0.55, 6.58, 7.9, PP_ALIGN.LEFT)
image(s, IMG / "captura7b.png", 8.7, 1.8, 4.05, 0.86)
caption(s, "ZIP descargado (~4,5 MB).", 8.7, 2.68, 4.05, PP_ALIGN.LEFT)
bullets(s, ["Modelo portable: inferencia local o en el borde, sin depender de Azure.",
            "También publicado como endpoint REST (hw7-iter1).",
            "Nivel F0: costo $0 durante todo el trabajo.",
            "Documentado y versionado en el repositorio."],
        8.7, 3.15, 4.1, 2.5, 11.5, TEXT, GREEN, gap=6)
rect(s, 8.7, 5.95, 4.1, 0.62, PANEL, BORDER, 0.9)
text(s, "Resultado: clasificador reproducible y exportable.", 8.9, 6.08, 3.75, 0.35, 10.5, GREEN, bold=True)
footer(s, 9)

# =====================================================================
# 10. CONCLUSIONES
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "Cierre", "Lo que aprendimos")
cols = [
    ("Funciona", GREEN, ["Clasificador sin código", "85% con imágenes nuevas", "ONNX portable", "Costo $0 (F0)"]),
    ("Cuidado", AMBER, ["3/10 gatos fallan", "La métrica interna es optimista", "Sesgo por fondo/contexto", "Dataset pequeño"]),
    ("Siguiente", CYAN, ["Más datos y augmentation", "Validación externa", "Monitoreo en producción", "Migrar a Azure ML AutoML (2028)"]),
]
for i, (title, color, items) in enumerate(cols):
    x = 0.55 + i * 4.12
    rect(s, x, 1.65, 3.9, 4.2, PANEL, BORDER, 0.9)
    rect(s, x, 1.65, 3.9, 0.07, color, shape=MSO_SHAPE.RECTANGLE)
    text(s, title, x + 0.25, 1.85, 3.4, 0.35, 16, color, bold=True)
    bullets(s, items, x + 0.25, 2.30, 3.35, 3.3, 13.5, TEXT, color, gap=12)
rect(s, 0.55, 6.1, 12.23, 0.75, PANEL2, BORDER, 0.9)
text(s, "“La métrica del portal no es el resultado final: la prueba con imágenes nuevas decide.”",
     0.8, 6.25, 11.7, 0.4, 14.5, TEXT, italic=True, align=PP_ALIGN.CENTER)
footer(s, 10)

# =====================================================================
# 11. CIERRE
# =====================================================================
s = prs.slides.add_slide(BLANK); bg(s, gradient=True)
text(s, "GRACIAS", 0.85, 1.05, 6.0, 0.3, 11, CYAN, bold=True)
text(s, "¿Preguntas?", 0.85, 1.45, 9.0, 0.95, 48, TEXT, bold=True)
text(s, "Clasificación de imágenes gatos vs. perros con Azure Custom Vision.", 0.85, 2.65, 9.0, 0.5, 16, MUTED)
rect(s, 0.85, 3.35, 2.2, 0.055, CYAN, shape=MSO_SHAPE.RECTANGLE)
stats = [("60", "train"), ("20", "hold-out"), ("85%", "accuracy"), ("$0", "costo F0")]
for i, (v, l) in enumerate(stats):
    x = 0.85 + i * 2.75
    text(s, v, x, 3.75, 2.2, 0.8, 32, CYAN if i != 2 else GREEN, bold=True)
    text(s, l, x, 4.55, 2.2, 0.3, 11, MUTED)
text(s, "Repositorio: github.com/andr3348/CloudTask", 0.85, 5.75, 9.0, 0.3, 12, TEXT, bold=True)
text(s, "SENATI · Tecnología Cloud · [Nombre Apellido] · Noviembre 2026", 0.85, 6.15, 9.5, 0.3, 10.5, MUTED)
text(s, "07", 9.0, 1.1, 3.8, 3.0, 190, RGBColor(0x16, 0x2D, 0x48), bold=True, align=PP_ALIGN.CENTER)


# ---------------- notas del expositor ----------------
NOTES = [
    "Saludo y presentación. TP07: Computer Vision con Azure Custom Vision, un clasificador gatos vs. perros sin código.",
    "Contexto: el reto, el alcance y por qué Custom Vision. Resaltar que se automatizó con CLI/REST y se exportó a ONNX.",
    "Recorrer el diagrama: dataset, Training F0, proyecto, iteración, Prediction F0, evaluación y exportación.",
    "Mostrar que los recursos existen en Azure: grupo de recursos, Training y Prediction en F0, claves protegidas.",
    "Explicar el dataset: 60 imágenes de entrenamiento balanceadas y 20 reservadas para la prueba real.",
    "La captura del portal muestra 100% en precisión, recall y AP sobre la validación interna. Aclarar que puede ser optimista.",
    "Prueba real: 85% de exactitud con 20 imágenes nuevas. Los perros se clasifican perfecto; los gatos concentran los errores.",
    "El error es evidencia: un gato con 68,5% de confianza como perro. Discutir fondos, poses y tamaño del dataset.",
    "El modelo se exporta a ONNX (~4,5 MB) y también queda publicado como endpoint REST. Costo total $0 con F0.",
    "Cerrar con las tres ideas: funciona, cuidado con la métrica interna y siguientes pasos (más datos, validación, monitoreo).",
    "Agradecer y abrir preguntas. Recordar el repositorio y los entregables.",
]
for slide, note in zip(prs.slides, NOTES):
    slide.notes_slide.notes_text_frame.text = note

prs.core_properties.title = "Computer Vision en Azure: clasificación gatos vs. perros"
prs.core_properties.subject = "Trabajo Práctico 07 - Azure Custom Vision"
prs.core_properties.author = "SENATI - Tecnología Cloud"
prs.core_properties.keywords = "Azure, Custom Vision, Computer Vision, AutoML, ONNX"

prs.save(OUT)
print("OK:", OUT)
