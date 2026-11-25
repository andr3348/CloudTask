#!/usr/bin/env python3
"""Genera el diagrama de arquitectura HW7 como PNG (matplotlib)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BLUE = "#0078D4"; DARK = "#323130"; GRAY = "#605E5C"
GREEN = "#107C10"; GOLD = "#986F0B"; RED = "#A4262C"

fig, ax = plt.subplots(figsize=(14, 8.6), dpi=220)
ax.set_xlim(0, 140); ax.set_ylim(0, 86); ax.axis("off")
fig.patch.set_facecolor("white")

def box(x, y, w, h, title, body="", fill="#FFFFFF", border=BLUE,
        tsize=10.8, bsize=8.6, lw=1.4, ty=0.64, by=0.28):
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
          lx=None, ly=None, fs=8.3):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=14, linewidth=lw, color=color,
                                 linestyle=ls, zorder=1, shrinkA=2, shrinkB=2))
    if label:
        ax.text(lx if lx is not None else (x1 + x2)/2,
                ly if ly is not None else (y1 + y2)/2 + 1.3,
                label, ha="center", va="center", fontsize=fs, color=color, zorder=4,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.9))

# Azure boundary
ax.add_patch(FancyBboxPatch((2, 2), 136, 81, boxstyle="round,pad=0.3,rounding_size=1.6",
                            linewidth=2, edgecolor=BLUE, facecolor="#F5FAFF", zorder=0))
ax.text(5, 80.3, "Microsoft Azure  ·  South Central US", fontsize=12.5,
        fontweight="bold", color=BLUE, zorder=5)

# Resource group
ax.add_patch(FancyBboxPatch((26, 8), 74, 66, boxstyle="round,pad=0.3,rounding_size=1.4",
                            linewidth=1.4, edgecolor="#8A8886", facecolor="#FAFAFA",
                            linestyle=(0, (4, 2)), zorder=0))
ax.text(63, 71.4, "Grupo de recursos: rg-cloudtask-hw7", ha="center", fontsize=10.2,
        fontweight="bold", color=GRAY, zorder=5)

# Dataset + CLI (outside RG, local)
box(3, 56, 20, 13, "Dataset Cats vs Dogs",
    "60 train (30 cats / 30 dogs)\n20 hold-out (10 / 10)", fill="#F3F2F1", border="#8A8886")
box(3, 36, 20, 10, "Automatización", "Azure CLI + REST\nCustom Vision v3.4-preview",
    fill="#EDEBE9", border="#8A8886", tsize=9.8, bsize=8.2)

# Custom Vision resources
box(32, 56, 26, 11, "Custom Vision Training",
    "cv-hw7-train-4632  ·  F0\nTraining-Key + endpoint", fill="#DEECF9", border=BLUE)
box(66, 56, 26, 11, "Custom Vision Prediction",
    "cv-hw7-pred-4632  ·  F0\nPrediction-Key + endpoint", fill="#DEECF9", border=BLUE)

# Project / iteration / export
box(32, 36, 26, 12, "Proyecto hw7-cats-vs-dogs",
    "General (compact)  ·  Multiclase\nEtiquetas: cats / dogs", fill="#E8F4FD", border=BLUE)
box(66, 36, 26, 12, "Iteración hw7-iter1",
    "Quick training (Regular)\nP 1.000  ·  R 0.9167  ·  AP 1.000",
    fill="#DDF3E4", border=GREEN)
box(66, 14, 26, 10, "Exportación ONNX",
    "hw7-cats-vs-dogs-onnx.zip\n4,4 MB", fill="#FFF4CE", border=GOLD, tsize=10)

# Evaluation panel
box(102, 32, 33, 35, "Evaluación hold-out",
    "Accuracy: 85 % (17/20)\n\n"
    "cats:  P 1.000  ·  R 0.700\ndogs:  P 0.769  ·  R 1.000\n\n"
    "Matriz de confusión\n"
    "           pred:cats   pred:dogs\n"
    "real:cats      7           3\n"
    "real:dogs      0          10",
    fill="#FDF3F4", border=RED, tsize=11.2, bsize=8.7, ty=0.82, by=0.43)

# Arrows (training / deployment)
arrow(23.3, 62.5, 31.7, 62.2, "60 imágenes + tags", lx=27.5, ly=65.4, fs=8.0)
arrow(45, 55.7, 45, 48.4, "crear / cargar", lx=45, ly=52.2)
arrow(58.3, 42, 65.7, 42, "entrenar", lx=62, ly=44.0)
arrow(79, 48.3, 79, 55.7, "publicar", lx=79, ly=52.2)
arrow(79, 35.7, 79, 24.3, "exportar", lx=79, ly=30.0)
arrow(92.3, 61.3, 101.7, 60.5, "predecir", lx=97, ly=63.6, fs=7.8)

# CLI -> resources (dashed)
arrow(23.2, 44.5, 31.7, 58.5, "API", color="#8A8886", ls=(0, (3, 2)), lx=27.6, ly=50.5, fs=7.8)

# Hold-out -> evaluation (top route)
xs, ys = [13, 13, 118.5, 118.5], [69.3, 78.8, 78.8, 67.6]
ax.plot(xs[:-1], ys[:-1], color=RED, lw=1.4, ls=(0, (3, 2)), zorder=1)
arrow(xs[-2], ys[-2], xs[-1], ys[-1], "", color=RED, ls=(0, (3, 2)), lw=1.4)
ax.text(66, 80.0, "20 imágenes hold-out (evaluación)", ha="center", fontsize=8.4,
        color=RED, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))

# Legend
ax.text(5, 27, "Flujo sólido: entrenamiento y despliegue", fontsize=8.4, color=GRAY)
ax.text(5, 23.5, "Flujo punteado: automatización y evaluación", fontsize=8.4, color=GRAY)

plt.tight_layout(pad=0.2)
out = "/home/andree/projects/college/cloud-task/docs/assets/hw7-architecture.png"
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("OK:", out)
