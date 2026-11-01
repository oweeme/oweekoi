#!/usr/bin/env python3
"""Genera los esquemas de color de KDE (OweeKoiDark.colors y OweeKoiLight.colors) desde paleta.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paleta import CLARO, OSCURO, a_rgb, contraste  # noqa: E402

SALIDA = Path(__file__).resolve().parent.parent / "colores"


def rgb(h):
    return "%d,%d,%d" % a_rgb(h)


def grupo(nombre, fondo, alterno, P, texto=None):
    t = texto or P["texto"]
    return f"""[Colors:{nombre}]
BackgroundAlternate={rgb(alterno)}
BackgroundNormal={rgb(fondo)}
DecorationFocus={rgb(P['acento'])}
DecorationHover={rgb(P['acento'])}
ForegroundActive={rgb(P['coral'])}
ForegroundInactive={rgb(P['suave'])}
ForegroundLink={rgb(P['enlace'])}
ForegroundNegative={rgb(P['coral'])}
ForegroundNeutral={rgb(P['neutro'])}
ForegroundNormal={rgb(t)}
ForegroundPositive={rgb(P['positivo'])}
ForegroundVisited={rgb(P['visitado'])}
"""


def esquema(nombre, P, complementario):
    sel = f"""[Colors:Selection]
BackgroundAlternate={rgb(P['seleccion'])}
BackgroundNormal={rgb(P['seleccion'])}
DecorationFocus={rgb(P['acento'])}
DecorationHover={rgb(P['acento'])}
ForegroundActive={rgb(P['sobre_seleccion'])}
ForegroundInactive={rgb(P['sobre_seleccion'])}
ForegroundLink={rgb(P['sobre_seleccion'])}
ForegroundNegative={rgb(P['sobre_seleccion'])}
ForegroundNeutral={rgb(P['sobre_seleccion'])}
ForegroundNormal={rgb(P['sobre_seleccion'])}
ForegroundPositive={rgb(P['sobre_seleccion'])}
ForegroundVisited={rgb(P['sobre_seleccion'])}
"""
    partes = [
        grupo("Button", P["elevado"], P["superficie"], P),
        grupo("Complementary", complementario["base"], complementario["superficie"], complementario),
        grupo("Header", P["superficie"], P["base"], P),
        sel,
        grupo("Tooltip", P["elevado"], P["superficie"], P),
        grupo("View", P["vista"], P["superficie"], P),
        grupo("Window", P["base"], P["superficie"], P),
    ]
    resto = f"""[General]
ColorScheme={nombre}
Name={nombre.replace('OweeKoi', 'OweeKoi ')}
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={rgb(P['superficie'])}
activeBlend={rgb(P['superficie'])}
activeForeground={rgb(P['texto'])}
inactiveBackground={rgb(P['base'])}
inactiveBlend={rgb(P['base'])}
inactiveForeground={rgb(P['suave'])}
"""
    return "\n".join(partes) + "\n" + resto


def comprobar(nombre, P):
    pares = [("texto", "base", 4.5), ("texto", "vista", 4.5), ("texto", "elevado", 4.5),
             ("suave", "base", 4.5), ("sobre_seleccion", "seleccion", 4.5), ("enlace", "base", 4.5),
             ("positivo", "base", 4.5), ("neutro", "base", 4.5),
             ("acento", "base", 3.0)]  # el acento es un borde/relleno, no texto: basta 3:1
    malos = [(a, b, round(contraste(P[a], P[b]), 2)) for a, b, minimo in pares
             if contraste(P[a], P[b]) < minimo]
    return nombre, malos


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, P, comp in (("OweeKoiDark", OSCURO, OSCURO), ("OweeKoiLight", CLARO, OSCURO)):
        (SALIDA / f"{nombre}.colors").write_text(esquema(nombre, P, comp), encoding="utf-8")
        _, malos = comprobar(nombre, P)
        print(f"{nombre}.colors", "OK (todo AA)" if not malos else f"BAJO CONTRASTE: {malos}")
