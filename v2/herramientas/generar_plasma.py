#!/usr/bin/env python3
"""Estilo de Plasma propio de OweeKoi 2 ("Onda"): paneles, ventanas emergentes y dialogos.

Dibujo original, sin partir de ningun otro tema; solo se respeta el formato de piezas que
exige Plasma (center, top, topleft... mas pistas hint-* y la malla shadow-*/mask-*).
Los colores NO van fijos: se usan las clases ColorScheme-Background y ColorScheme-Text, que
Plasma sustituye por el esquema activo, asi un solo tema sirve para tinta y para papel.
Lo que este tema no define lo toma Plasma de su tema por defecto (Breeze), no de WhiteSur.

Lecciones aprendidas con el decorado de ventanas: QtSvg ignora clipPath, asi que cada pieza se
calcula como forma propia (arcos y rectangulos), sin recortar un dibujo grande.

Rasgo OweeKoi: la doble linea de onda (un borde fino y otro mas tenue 3 px dentro).

Salida: v2/plasma/desktoptheme/OweeKoi-Onda/
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "plasma" / "desktoptheme" / "OweeKoi-Onda"

ESTILO = ('<style type="text/css" id="current-color-scheme">'
          '.ColorScheme-Text{color:#ece6d6;}.ColorScheme-Background{color:#2d2a2c;}</style>')


def pieza_forma(nombre, S, E, ins, radios):
    """Camino del cuerpo dentro de una pieza. ins=(arriba,abajo,izq,der), radios=(tl,tr,bl,br)."""
    it, ib, il, ir = ins
    rtl, rtr, rbl, rbr = radios
    w = {"l": S, "c": E, "r": S}
    h = {"t": S, "m": E, "b": S}
    f, c = nombre
    W, H = w[c], h[f]
    if nombre == "tl":
        r = rtl
        return f"M{il} {H}L{il} {it + r}A{r} {r} 0 0 1 {il + r} {it}L{W} {it}L{W} {H}Z", W, H
    if nombre == "tc":
        return f"M0 {H}L0 {it}L{W} {it}L{W} {H}Z", W, H
    if nombre == "tr":
        r = rtr
        return f"M0 {H}L0 {it}L{W - ir - r} {it}A{r} {r} 0 0 1 {W - ir} {it + r}L{W - ir} {H}Z", W, H
    if nombre == "ml":
        return f"M{il} 0L{W} 0L{W} {H}L{il} {H}Z", W, H
    if nombre == "mc":
        return f"M0 0L{W} 0L{W} {H}L0 {H}Z", W, H
    if nombre == "mr":
        return f"M0 0L{W - ir} 0L{W - ir} {H}L0 {H}Z", W, H
    if nombre == "bl":
        r = rbl
        return f"M{il} 0L{il} {H - ib - r}A{r} {r} 0 0 0 {il + r} {H - ib}L{W} {H - ib}L{W} 0Z", W, H
    if nombre == "bc":
        return f"M0 0L0 {H - ib}L{W} {H - ib}L{W} 0Z", W, H
    r = rbr
    return f"M{W - ir} 0L{W - ir} {H - ib - r}A{r} {r} 0 0 1 {W - ir - r} {H - ib}L0 {H - ib}L0 0Z", W, H


def pieza_linea(nombre, S, E, ins, radios, off):
    """Linea fina a 'off' px dentro del borde del cuerpo (solo en los lados del marco)."""
    it, ib, il, ir = (v + off for v in ins)
    rtl, rtr, rbl, rbr = (max(r - off, 0) for r in radios)
    w = {"l": S, "c": E, "r": S}
    h = {"t": S, "m": E, "b": S}
    f, c = nombre
    W, H = w[c], h[f]
    if nombre == "tl":
        return f"M{il} {H}L{il} {it + rtl}A{rtl} {rtl} 0 0 1 {il + rtl} {it}L{W} {it}"
    if nombre == "tc":
        return f"M0 {it}L{W} {it}"
    if nombre == "tr":
        return f"M0 {it}L{W - ir - rtr} {it}A{rtr} {rtr} 0 0 1 {W - ir} {it + rtr}L{W - ir} {H}"
    if nombre == "ml":
        return f"M{il} 0L{il} {H}"
    if nombre == "mr":
        return f"M{W - ir} 0L{W - ir} {H}"
    if nombre == "bl":
        return f"M{il} 0L{il} {H - ib - rbl}A{rbl} {rbl} 0 0 0 {il + rbl} {H - ib}L{W} {H - ib}"
    if nombre == "bc":
        return f"M0 {H - ib}L{W} {H - ib}"
    if nombre == "br":
        return f"M{W - ir} 0L{W - ir} {H - ib - rbr}A{rbr} {rbr} 0 0 1 {W - ir - rbr} {H - ib}L0 {H - ib}"
    return ""


ORDEN = [["tl", "tc", "tr"], ["ml", "mc", "mr"], ["bl", "bc", "br"]]
NOMBRE = {"tl": "topleft", "tc": "top", "tr": "topright", "ml": "left", "mc": "center",
          "mr": "right", "bl": "bottomleft", "bc": "bottom", "br": "bottomright"}


def conjunto(prefijo, ox, oy, S, E, ins, radios, opacidad, estilo, id_grad):
    """Un juego de 9 piezas. estilo: 'cuerpo' | 'mascara' | 'sombra'."""
    out = []
    y = oy
    for fila in ORDEN:
        x = ox
        for p in fila:
            d, W, H = pieza_forma(p, S, E, ins, radios)
            if estilo == "cuerpo":
                cuerpo = (f'<path d="{d}" class="ColorScheme-Background" fill="currentColor" '
                          f'fill-opacity="{opacidad}"/>')
                # doble linea de onda: borde fino y otro mas tenue 3 px dentro
                for off, op in ((0.5, 0.20), (3.5, 0.08)):
                    ln = pieza_linea(p, S, E, ins, radios, off)
                    if ln:
                        cuerpo += (f'<path d="{ln}" fill="none" class="ColorScheme-Text" stroke="currentColor" '
                                   f'stroke-opacity="{op}" stroke-width="1"/>')
            elif estilo == "mascara":
                cuerpo = f'<path d="{d}" fill="#000"/>'
            else:
                cuerpo = sombra_pieza(p, W, H, f"{id_grad}{prefijo}")
            # el rectangulo casi transparente fija el tamano exacto de la pieza
            out.append(f'<g id="{prefijo}{NOMBRE[p]}" transform="translate({x} {y})">'
                       f'<rect width="{W}" height="{H}" fill="#000" fill-opacity="0.01"/>{cuerpo}</g>')
            x += W
        y += {"t": S, "m": E, "b": S}[fila[0][0]]
    return "".join(out), ox + 2 * S + E, oy + 2 * S + E


def sombra_pieza(p, W, H, id_grad):
    """Sombra: degradado de 0 (lejos del cuerpo) a su maximo (junto a el)."""
    a0 = 0.34
    gid = f"g{id_grad}{p}"
    if p == "mc":
        return ""  # debajo del cuerpo no hay sombra (el panel es translucido)
    if p in ("tl", "tr", "bl", "br"):
        cx = W if p in ("tl", "bl") else 0   # centro: la esquina interior de la pieza
        cy = H if p in ("tl", "tr") else 0
        paradas = "".join(f'<stop offset="{o}" stop-color="#000" stop-opacity="{a0 * v:.3f}"/>'
                          for o, v in ((0, 1), (0.40, 0.40), (0.70, 0.10), (1, 0)))
        return (f'<defs><radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" '
                f'r="{W}">{paradas}</radialGradient></defs><rect width="{W}" height="{H}" fill="url(#{gid})"/>')
    paradas = "".join(f'<stop offset="{o}" stop-color="#000" stop-opacity="{a0 * v:.3f}"/>'
                      for o, v in ((0, 0), (0.30, 0.10), (0.60, 0.40), (1, 1)))
    if p == "tc":
        x1, y1, x2, y2 = 0, 0, 0, H          # de arriba (fuera) hacia abajo (cuerpo)
    elif p == "bc":
        x1, y1, x2, y2 = 0, H, 0, 0
    elif p == "ml":
        x1, y1, x2, y2 = 0, 0, W, 0
    else:  # mr
        x1, y1, x2, y2 = W, 0, 0, 0
    return (f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}">{paradas}</linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>')


def pistas(prefijo, ox, oy, S, E, margen, inset, prefijo_hint=""):
    """Rectangulos que declaran margenes e insets (solo importa su tamano)."""
    cx, cy = ox + S, oy + S
    def r(nombre, x, y, w, h):
        return f'<rect id="{prefijo}{prefijo_hint}{nombre}" x="{x}" y="{y}" width="{w}" height="{h}" fill="#ff00ff"/>'
    return "".join([
        r("hint-top-margin", cx + 4, oy, 4, margen), r("hint-bottom-margin", cx + 4, oy + 2 * S + E - margen, 4, margen),
        r("hint-left-margin", ox, cy + 4, margen, 4), r("hint-right-margin", ox + 2 * S + E - margen, cy + 4, margen, 4),
        r("hint-top-inset", cx - 4, oy, 4, inset), r("hint-bottom-inset", cx - 4, oy + 2 * S + E - inset, 4, inset),
        r("hint-left-inset", ox, cy - 4, inset, 4), r("hint-right-inset", ox + 2 * S + E - inset, cy - 4, inset, 4),
    ])


def svg_marco(S, E, I, R, margen, inset, S_sombra, opacidad, prefijos_panel=False, solido=False):
    """Un archivo completo. prefijos_panel: ademas de plano, versiones north/south/east/west."""
    op = 1 if solido else opacidad
    ins_all = (I, I, I, I)
    radios_all = (R, R, R, R)
    variantes = [("", ins_all, radios_all)]
    if prefijos_panel:
        variantes += [
            ("north-", (0, I, I, I), (0, 0, R, R)), ("south-", (I, 0, I, I), (R, R, 0, 0)),
            ("west-", (I, I, 0, I), (0, R, 0, R)), ("east-", (I, I, I, 0), (R, 0, R, 0)),
        ]
    partes, x, y = [], 10, 10
    for pref, ins, radios in variantes:
        cuerpo, nx, _ = conjunto(pref, x, y, S, E, ins, radios, op, "cuerpo", "c")
        mascara, mx, _ = conjunto(pref + "mask-", nx + 20, y, S, E, ins, radios, 1, "mascara", "m")
        partes += [cuerpo, mascara, pistas(pref, x, y, S, E, margen, inset)]
        y += 2 * S + E + 20
    # malla de sombra (una sola, para el juego plano)
    sombra, _, _ = conjunto("shadow-", 10 + 2 * (2 * S + E + 20) + 40, 10, S_sombra, E, (0, 0, 0, 0),
                            (0, 0, 0, 0), 1, "sombra", "s")
    partes += [sombra, pistas("shadow-", 10 + 2 * (2 * S + E + 20) + 40, 10, S_sombra, E, S_sombra // 2, S_sombra // 2)]
    ancho = 10 + 2 * (2 * S + E + 20) + 40 + 2 * S_sombra + E + 20
    alto = 10 + len(variantes) * (2 * S + E + 20)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}">{ESTILO}'
            f'{"".join(partes)}</svg>')


METADATA = """{
    "KPackageStructure": "Plasma/Theme",
    "KPlugin": {
        "Authors": [{ "Name": "Owee" }],
        "Category": "",
        "Description": "OweeKoi Onda: paneles y ventanas emergentes con doble linea de onda. Sigue el esquema claro u oscuro.",
        "EnabledByDefault": true,
        "Id": "OweeKoi-Onda",
        "License": "GPL-3.0+",
        "Name": "OweeKoi Onda",
        "Version": "1.0"
    }
}
"""


def escribir(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    import shutil
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    # panel: piezas de 12 px, cuerpo a ras (el panel flotante deja su propio hueco)
    panel = svg_marco(12, 12, 0, 12, 8, 8, 24, 0.90, prefijos_panel=True)
    # ventana emergente y dialogos: piezas de 24 px con el cuerpo 12 px adentro
    emergente = svg_marco(24, 20, 12, 12, 24, 12, 24, 0.97)
    escribir(DESTINO / "metadata.json", METADATA)
    escribir(DESTINO / "widgets" / "panel-background.svg", panel)
    escribir(DESTINO / "widgets" / "background.svg", emergente)
    escribir(DESTINO / "dialogs" / "background.svg", emergente)
    escribir(DESTINO / "solid" / "widgets" / "background.svg", svg_marco(24, 20, 12, 12, 24, 12, 24, 1, solido=True))
    escribir(DESTINO / "solid" / "dialogs" / "background.svg", svg_marco(24, 20, 12, 12, 24, 12, 24, 1, solido=True))
    escribir(DESTINO / "LEEME.txt",
             "OweeKoi Onda: estilo de Plasma propio de Owee (GPL-3.0). Lo que no define lo toma el tema por defecto.\n")
    print(f"plasma/desktoptheme/OweeKoi-Onda  ({sum(1 for _ in DESTINO.rglob('*.svg'))} svg)")
