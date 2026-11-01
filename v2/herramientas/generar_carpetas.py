#!/usr/bin/env python3
"""Genera las carpetas de colores (SVG) del tema de iconos OweeKoi desde paleta.py.

Estilo plano y suave, parecido al de macOS: hoja trasera mas oscura, hoja frontal con
degradado leve y un brillo fino arriba. Un solo juego sirve para modo claro y oscuro.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paleta import CARPETAS, color_carpeta  # noqa: E402

SALIDA = Path(__file__).resolve().parent.parent / "iconos" / "OweeKoi" / "places" / "scalable"

PLANTILLA = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="frente" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{claro}"/>
      <stop offset="1" stop-color="{base}"/>
    </linearGradient>
  </defs>
  <path d="M8 14a4 4 0 0 1 4-4h12.6a4 4 0 0 1 2.9 1.2l2.6 2.8H52a4 4 0 0 1 4 4v8H8z" fill="{atras}"/>
  <rect x="6" y="19" width="52" height="35" rx="5" fill="url(#frente)"/>
  <path d="M11 19.6h42" stroke="#ffffff" stroke-opacity=".38" stroke-width="1.2" stroke-linecap="round"/>
  <rect x="6" y="19" width="52" height="35" rx="5" fill="none" stroke="{borde}" stroke-opacity=".35"/>
</svg>
"""


def mezcla(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def svg(color):
    return PLANTILLA.format(
        base=color, claro=mezcla(color, "#ffffff", 0.22), atras=mezcla(color, "#000000", 0.28),
        borde=mezcla(color, "#000000", 0.5))


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre in [*CARPETAS, "gris"]:
        color = color_carpeta(nombre)
        (SALIDA / f"folder-owee-{nombre}.svg").write_text(svg(color), encoding="utf-8")
        print(f"folder-owee-{nombre}.svg  {color}")
