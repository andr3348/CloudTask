#!/usr/bin/env python3
"""Genera el diagrama de arquitectura HW8 (Azure AI Language: Text Analytics + CLU) como PNG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BLUE = "#0078D4"
DARK = "#323130"
GRAY = "#605E5C"
GREEN = "#107C10"
GOLD = "#986F0B"
PURPLE = "#5C2D91"

fig, ax = plt.subplots(figsize=(14, 8.6), dpi=220)
ax.set_xlim(0, 140)
ax.set_ylim(0, 86)
ax.axis("off")
fig.patch.set_facecolor("white")


def box(x, y, w, h, title, body="", fill="#FFFFFF", border=BLUE,
        tsize=10.6, bsize=8.5, lw=1.4, ty=0.68, by=0.30):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.1",
                                linewidth=lw, edgecolor=border, facecolor=fill, zorder=2))
    if body:
        ax.text(x + w/2, y + h*ty, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color=DARK, zorder=3)
        ax.text(x + w/2, y + h*by, body, ha="center", va="center",
                fontsize=bsize, color=DARK, linespacing=1.35, zorder=3)
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center",
                fontsize=tsize, fontweight="bold", color=DARK, zorder=3)


def arrow(x1, y1, x2, y2, label="", color=GRAY, style="-|>", lw=1.6, ls="-",
          lx=None, ly=None, fs=8.2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=14, linewidth=lw, color=color,
                                 linestyle=ls, zorder=1, shrinkA=2, shrinkB=2))
    if label:
        ax.text(lx if lx is not None else (x1 + x2)/2,
                ly if ly is not None else (y1 + y2)/2 + 1.3,
                label, ha="center", va="center", fontsize=fs, color=color, zorder=4,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.92))


# Azure boundary
ax.add_patch(FancyBboxPatch((2, 2), 136, 81, boxstyle="round,pad=0.3,rounding_size=1.6",
                            linewidth=2, edgecolor=BLUE, facecolor="#F5FAFF", zorder=0))
ax.text(5, 80.3, "Microsoft Azure  ·  South Central US  (Azure for Students)",
        fontsize=12.2, fontweight="bold", color=BLUE, zorder=5)

# Resource group
ax.add_patch(FancyBboxPatch((28, 7), 73, 68, boxstyle="round,pad=0.3,rounding_size=1.4",
                            linewidth=1.4, edgecolor="#8A8886", facecolor="#FAFAFA",
                            linestyle=(0, (4, 2)), zorder=0))
ax.text(64.5, 72.4, "Grupo de recursos: rg-cloudtask-hw8  |  Recurso: lang-hw8-4632 (TextAnalytics · F0)",
        ha="center", fontsize=9.8, fontweight="bold", color=GRAY, zorder=5)

# Left local inputs
box(4, 56, 21, 13, "Textos de prueba (NLP)",
    "6 reseñas y mensajes\n(es / en / pt)\nText Analytics REST",
    fill="#F3F2F1", border="#8A8886")
box(4, 34, 21, 14, "Dataset Restaurante CLU",
    "64 frases (6 intenciones,\n5 entidades, UTF-16)\n+ 18 frases hold-out",
    fill="#F3F2F1", border="#8A8886")
box(4, 13, 21, 12, "Automatización CLI/REST",
    "Azure CLI + Python\napi-version 2023-04-01",
    fill="#EDEBE9", border="#8A8886", tsize=9.8, bsize=8.2)

# Top lane: Text Analytics
box(33, 56, 63, 12, "Azure AI Language — Text Analytics (:analyze-text)",
    "LanguageDetection (es, en, pt: 1.00)  ·  SentimentAnalysis + Opinion Mining\n"
    "EntityRecognition (NER: Person, Location, Org, Product)  ·  KeyPhraseExtraction",
    fill="#DEECF9", border=BLUE, tsize=10.6, bsize=8.4, ty=0.68, by=0.32)

# Bottom lane: CLU Authoring & Runtime
box(33, 35, 28, 13, "CLU Authoring (:import / :train)",
    "Proyecto: hw8-restaurante-luis\nModelo v1 (advanced, 80/20)\nIntents F1: 0.917 · Entities: 0.737",
    fill="#E8F4FD", border=BLUE)
box(68, 35, 28, 13, "CLU Runtime (Deployment)",
    "Despliegue: production\nEndpoint :analyze-conversations\nTop intent + confidence + entities",
    fill="#DDF3E4", border=GREEN)
box(33, 13, 28, 12, "Exportación del modelo",
    "POST :export (Utf16CodeUnit)\nhw8-restaurante-luis-export.json\n21,370 bytes",
    fill="#FFF4CE", border=GOLD, tsize=10.0)
box(68, 13, 28, 12, "Lógica Chatbot Restaurante",
    "RealizarPedido · ConsultarMenu\nReservarMesa · HorarioUbicacion\nCancelarPedido · None",
    fill="#F3EBF9", border=PURPLE, tsize=10.0)

# Right panel: Results
box(105, 16, 30, 52, "Resultados verificados",
    "Text Analytics (6 docs)\n"
    "• Idioma: 100 % (es/en/pt)\n"
    "• Sentimiento: pos 0.99 / neg 0.97\n"
    "• NER + Key Phrases extraídas\n\n"
    "CLU Hold-out (18 frases)\n"
    "• Accuracy: 18/18 = 100.0 %\n"
    "• 'Quiero pedir una pizza'\n"
    "  -> RealizarPedido (0.9999)\n"
    "  -> Cantidad='una', Plato='pizza'\n"
    "• '¿Cuál es el menú de hoy?'\n"
    "  -> ConsultarMenu (0.9998)",
    fill="#FDFDFD", border=GREEN, tsize=11.0, bsize=8.2, ty=0.87, by=0.43)

# Arrows
arrow(25.3, 62.5, 32.7, 62.5, "POST docs", lx=29, ly=65.0)
arrow(25.3, 41.0, 32.7, 41.5, "64 frases", lx=29, ly=44.2)
arrow(61.3, 41.5, 67.7, 41.5, "deploy", lx=64.5, ly=43.8)
arrow(47.0, 34.7, 47.0, 25.3, "exportar", lx=47.0, ly=30.0)
arrow(82.0, 34.7, 82.0, 25.3, "intent + ents", lx=82.0, ly=30.0)
arrow(96.3, 61.5, 104.7, 56.0, "JSON", lx=100.5, ly=61.0)
arrow(96.3, 41.5, 104.7, 41.5, "18 test", lx=100.5, ly=44.0)
arrow(25.3, 19.0, 32.7, 37.0, "REST", color="#8A8886", ls=(0, (3, 2)), lx=28.5, ly=26.0)

# Hold-out top dashed route
xs, ys = [14.5, 14.5, 82.0, 82.0], [48.3, 52.0, 52.0, 48.3]
ax.plot(xs[:-1], ys[:-1], color=GREEN, lw=1.3, ls=(0, (3, 2)), zorder=1)
arrow(xs[-2], ys[-2], xs[-1], ys[-1], "", color=GREEN, ls=(0, (3, 2)), lw=1.3)
ax.text(48, 53.3, "18 frases hold-out -> evaluación en producción", ha="center", fontsize=8.1,
        color=GREEN, bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none"))

plt.tight_layout(pad=0.4)
plt.savefig("docs/assets/hw8-architecture.png", dpi=220)
print("Diagrama guardado en docs/assets/hw8-architecture.png")
