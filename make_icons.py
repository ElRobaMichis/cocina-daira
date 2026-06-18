#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera los iconos PWA (plato + aguacate sobre terracota). Render a 4x y baja para antialias."""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT, exist_ok=True)

TERRA = (189, 90, 53)       # primary terracotta
TERRA_D = (150, 68, 38)
CREAM = (253, 250, 243)
PLATE_RIM = (240, 232, 218)
AVO = (95, 150, 80)
AVO_LITE = (175, 205, 130)
PIT = (150, 96, 52)


def rrect(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def draw_icon(size, maskable=False):
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # fondo
    if maskable:
        d.rectangle([0, 0, S, S], fill=TERRA)          # full-bleed para la máscara
        cx = cy = S / 2
        plate_r = S * 0.30
    else:
        rrect(d, [0, 0, S, S], r=S * 0.23, fill=TERRA)
        cx = cy = S / 2
        plate_r = S * 0.34

    # sombra suave del plato
    d.ellipse([cx - plate_r * 1.02, cy - plate_r * 0.92,
               cx + plate_r * 1.02, cy + plate_r * 1.12], fill=TERRA_D)
    # plato
    d.ellipse([cx - plate_r, cy - plate_r, cx + plate_r, cy + plate_r], fill=CREAM)
    d.ellipse([cx - plate_r * 0.82, cy - plate_r * 0.82,
               cx + plate_r * 0.82, cy + plate_r * 0.82], outline=PLATE_RIM, width=int(S * 0.006))

    # aguacate (mitad)
    aw, ah = plate_r * 0.62, plate_r * 0.82
    d.ellipse([cx - aw, cy - ah, cx + aw, cy + ah], fill=AVO)
    d.ellipse([cx - aw * 0.72, cy - ah * 0.72, cx + aw * 0.72, cy + ah * 0.72], fill=AVO_LITE)
    pr = plate_r * 0.26
    d.ellipse([cx - pr, cy - pr * 0.7, cx + pr, cy + pr * 1.3], fill=PIT)

    img = img.resize((size, size), Image.LANCZOS)
    return img


draw_icon(192).save(os.path.join(OUT, "icon-192.png"))
draw_icon(512).save(os.path.join(OUT, "icon-512.png"))
draw_icon(512, maskable=True).save(os.path.join(OUT, "icon-maskable.png"))
draw_icon(192, maskable=True).save(os.path.join(OUT, "icon-maskable-192.png"))
draw_icon(180).save(os.path.join(OUT, "apple-touch-icon.png"))
draw_icon(32).save(os.path.join(OUT, "favicon-32.png"))
print("Iconos generados en", OUT)
