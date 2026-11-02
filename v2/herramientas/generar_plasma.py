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


def pieza_banda(nombre, S, E, ins, radios, b):
    """Banda rellena de 1 px a 'b' px dentro del borde del cuerpo, como forma cerrada.

    Se usan formas rellenas y no trazos: Qt suma medio pixel de trazo a cada lado al medir una
    pieza, y eso las agranda (24 -> 25) y descuadra el marco entero."""
    it, ib, il, ir = ins
    rtl, rtr, rbl, rbr = radios
    t = 1
    w = {"l": S, "c": E, "r": S}
    h = {"t": S, "m": E, "b": S}
    if nombre == "mc":
        return ""  # el centro no lleva lineas
    f, c = nombre
    W, H = w[c], h[f]
    xl, xr, yt, yb = il + b, W - ir - b, it + b, H - ib - b

    def arcos(r):
        ro = r - b
        return ro, ro - t

    if nombre == "tl":
        if rtl > b + t:
            ro, ri = arcos(rtl)
            return (f"M{xl} {H}L{xl} {it + rtl}A{ro} {ro} 0 0 1 {il + rtl} {yt}L{W} {yt}L{W} {yt + t}"
                    f"L{il + rtl} {yt + t}A{ri} {ri} 0 0 0 {xl + t} {it + rtl}L{xl + t} {H}Z")
        return f"M{xl} {H}L{xl} {yt}L{W} {yt}L{W} {yt + t}L{xl + t} {yt + t}L{xl + t} {H}Z"
    if nombre == "tc":
        return f"M0 {yt}L{W} {yt}L{W} {yt + t}L0 {yt + t}Z"
    if nombre == "tr":
        if rtr > b + t:
            ro, ri = arcos(rtr)
            return (f"M0 {yt}L{W - ir - rtr} {yt}A{ro} {ro} 0 0 1 {xr} {it + rtr}L{xr} {H}L{xr - t} {H}"
                    f"L{xr - t} {it + rtr}A{ri} {ri} 0 0 0 {W - ir - rtr} {yt + t}L0 {yt + t}Z")
        return f"M0 {yt}L{xr} {yt}L{xr} {H}L{xr - t} {H}L{xr - t} {yt + t}L0 {yt + t}Z"
    if nombre == "ml":
        return f"M{xl} 0L{xl + t} 0L{xl + t} {H}L{xl} {H}Z"
    if nombre == "mr":
        return f"M{xr - t} 0L{xr} 0L{xr} {H}L{xr - t} {H}Z"
    if nombre == "bl":
        if rbl > b + t:
            ro, ri = arcos(rbl)
            return (f"M{xl} 0L{xl} {H - ib - rbl}A{ro} {ro} 0 0 0 {il + rbl} {yb}L{W} {yb}L{W} {yb - t}"
                    f"L{il + rbl} {yb - t}A{ri} {ri} 0 0 1 {xl + t} {H - ib - rbl}L{xl + t} 0Z")
        return f"M{xl} 0L{xl} {yb}L{W} {yb}L{W} {yb - t}L{xl + t} {yb - t}L{xl + t} 0Z"
    if nombre == "bc":
        return f"M0 {yb - t}L{W} {yb - t}L{W} {yb}L0 {yb}Z"
    if rbr > b + t:  # br
        ro, ri = arcos(rbr)
        return (f"M{xr} 0L{xr} {H - ib - rbr}A{ro} {ro} 0 0 1 {W - ir - rbr} {yb}L0 {yb}L0 {yb - t}"
                f"L{W - ir - rbr} {yb - t}A{ri} {ri} 0 0 0 {xr - t} {H - ib - rbr}L{xr - t} 0Z")
    return f"M{xr} 0L{xr} {yb}L0 {yb}L0 {yb - t}L{xr - t} {yb - t}L{xr - t} 0Z"


ORDEN = [["tl", "tc", "tr"], ["ml", "mc", "mr"], ["bl", "bc", "br"]]
NOMBRE = {"tl": "topleft", "tc": "top", "tr": "topright", "ml": "left", "mc": "center",
          "mr": "right", "bl": "bottomleft", "bc": "bottom", "br": "bottomright"}


def conjunto(prefijo, ox, oy, S, E, ins, radios, opacidad, estilo, id_grad, bandas=((0, 0.20), (3, 0.08)),
             anillo=False, sombra_modo="externa"):
    """Un juego de 9 piezas. estilo: 'cuerpo' | 'mascara' | 'sombra'."""
    out = []
    y = oy
    for fila in ORDEN:
        x = ox
        for p in fila:
            d, W, H = pieza_forma(p, S, E, ins, radios)
            if estilo == "cuerpo":
                # sombra pegada al cuerpo (en el anillo transparente del marco), redondeada como el
                cuerpo = ""
                if anillo:
                    # base: sombra casi imperceptible; encima, tres anillos de onda cada vez mas tenues
                    cuerpo = sombra_pieza(p, W, H, f"r{id_grad}{prefijo}", 0.09)
                    for b, op in ((-3, 0.10), (-6, 0.06), (-9, 0.03)):
                        halo = pieza_banda(p, S, E, ins, radios, b)
                        if halo:
                            cuerpo += (f'<path d="{halo}" class="ColorScheme-Text" fill="currentColor" '
                                       f'fill-opacity="{op}"/>')
                cuerpo += (f'<path d="{d}" class="ColorScheme-Background" fill="currentColor" '
                           f'fill-opacity="{opacidad}"/>')
                # doble linea de onda: borde fino y otro mas tenue 3 px dentro
                for b, op in bandas:
                    banda = pieza_banda(p, S, E, ins, radios, b)
                    if banda:
                        cuerpo += (f'<path d="{banda}" class="ColorScheme-Text" '
                                   f'fill="currentColor" fill-opacity="{op}"/>')
            elif estilo == "mascara":
                cuerpo = f'<path d="{d}" fill="#000"/>'
            else:
                cuerpo = "" if sombra_modo == "transparente" else sombra_completa(p, W, H, f"{id_grad}{prefijo}")
            # el rectangulo casi transparente fija el tamano exacto de la pieza
            out.append(f'<g id="{prefijo}{NOMBRE[p]}" transform="translate({x} {y})">'
                       f'<rect width="{W}" height="{H}" fill="none"/>{cuerpo}</g>')
            x += W
        y += {"t": S, "m": E, "b": S}[fila[0][0]]
    return "".join(out), ox + 2 * S + E, oy + 2 * S + E


def sombra_pieza(p, W, H, id_grad, a0=0.30, ancho=12, radio=12):
    """Sombra: anillo de 'ancho' px alrededor del cuerpo, con el hueco redondeado como el cuerpo.

    La pieza mide 2*ancho de lado en las esquinas: los primeros 'ancho' px son sombra y el resto
    es el hueco (donde esta el cuerpo). El desvanecido se mide desde el borde del hueco."""
    gid = f"g{id_grad}{p}"
    if p == "mc":
        return ""
    # perfil suave: de 0 (borde exterior) a a0 (junto al cuerpo)
    perfil = ((0, 0), (0.25, 0.09), (0.5, 0.30), (0.75, 0.62), (1, 1))
    if p in ("tl", "tr", "bl", "br"):
        cx = W if p in ("tl", "bl") else 0   # centro del arco del hueco
        cy = H if p in ("tl", "tr") else 0
        r_ext = ancho + radio                 # radio donde la sombra llega a 0
        f_hueco = radio / r_ext               # el hueco ocupa de 0 a este valor
        paradas = [f'<stop offset="0" stop-color="#000" stop-opacity="0"/>',
                   f'<stop offset="{f_hueco - 0.02:.3f}" stop-color="#000" stop-opacity="0"/>']
        for o, v in reversed(perfil):          # del hueco (maximo) hacia fuera (0)
            off = f_hueco + (1 - f_hueco) * (1 - o)
            paradas.append(f'<stop offset="{off:.3f}" stop-color="#000" stop-opacity="{a0 * v:.3f}"/>')
        return (f'<defs><radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" '
                f'r="{r_ext}">{"".join(paradas)}</radialGradient></defs>'
                f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>')
    paradas = "".join(f'<stop offset="{o}" stop-color="#000" stop-opacity="{a0 * v:.3f}"/>' for o, v in perfil)
    if p == "tc":      # franja de arriba: de fuera (0) hacia el cuerpo
        x1, y1, x2, y2, rx, ry, rw, rh = 0, 0, 0, ancho, 0, 0, W, ancho
    elif p == "bc":
        x1, y1, x2, y2, rx, ry, rw, rh = 0, H, 0, H - ancho, 0, H - ancho, W, ancho
    elif p == "ml":
        x1, y1, x2, y2, rx, ry, rw, rh = 0, 0, ancho, 0, 0, 0, ancho, H
    else:  # mr
        x1, y1, x2, y2, rx, ry, rw, rh = W, 0, W - ancho, 0, W - ancho, 0, ancho, H
    return (f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}">{paradas}</linearGradient></defs>'
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="url(#{gid})"/>')


def sombra_completa(p, W, H, id_grad, a0=0.07):
    """Sombra exterior: degradado de 0 (lejos) a a0 en todo el ancho de la pieza (para el panel)."""
    gid = f"g{id_grad}{p}"
    if p == "mc":
        return ""
    perfil = ((0, 0), (0.30, 0.10), (0.60, 0.40), (1, 1))
    paradas = "".join(f'<stop offset="{o}" stop-color="#000" stop-opacity="{a0 * v:.3f}"/>' for o, v in perfil)
    if p in ("tl", "tr", "bl", "br"):
        cx = W if p in ("tl", "bl") else 0
        cy = H if p in ("tl", "tr") else 0
        par = "".join(f'<stop offset="{o}" stop-color="#000" stop-opacity="{a0 * v:.3f}"/>'
                      for o, v in ((0, 1), (0.40, 0.40), (0.70, 0.10), (1, 0)))
        return (f'<defs><radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{W}">'
                f'{par}</radialGradient></defs><rect width="{W}" height="{H}" fill="url(#{gid})"/>')
    x1, y1, x2, y2 = {"tc": (0, 0, 0, H), "bc": (0, H, 0, 0), "ml": (0, 0, W, 0), "mr": (W, 0, 0, 0)}[p]
    return (f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}">{paradas}</linearGradient></defs><rect width="{W}" height="{H}" fill="url(#{gid})"/>')


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
        # sin esto Plasma REPITE las piezas de borde y en cada junta se ve un trazo cortado
        r("hint-stretch-borders", cx + 12, cy + 12, 4, 4),
    ])


def svg_marco(S, E, I, R, margen, inset, S_sombra, opacidad, prefijos_panel=False, solido=False,
              bandas=((0, 0.20), (3, 0.08)), sombra="externa"):
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
        cuerpo, nx, _ = conjunto(pref, x, y, S, E, ins, radios, op, "cuerpo", "c", bandas,
                                  anillo=(sombra == "anillo"))
        mascara, mx, _ = conjunto(pref + "mask-", nx + 20, y, S, E, ins, radios, 1, "mascara", "m")
        partes += [cuerpo, mascara, pistas(pref, x, y, S, E, margen, inset)]
        y += 2 * S + E + 20
    # malla de sombra (una sola, para el juego plano)
    sombra, _, _ = conjunto("shadow-", 10 + 2 * (2 * S + E + 20) + 40, 10, S_sombra, E, (0, 0, 0, 0),
                            (0, 0, 0, 0), 1, "sombra", "s",
                            sombra_modo="transparente" if sombra == "anillo" else "externa")
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
    panel = svg_marco(8, 8, 0, 8, 8, 8, 24, 0.90, prefijos_panel=True, bandas=((0, 0.16),))
    # ventana emergente y dialogos: piezas de 24 px con el cuerpo 12 px adentro
    emergente = svg_marco(24, 20, 12, 12, 24, 12, 24, 0.97, sombra="anillo")
    escribir(DESTINO / "metadata.json", METADATA)
    escribir(DESTINO / "widgets" / "panel-background.svg", panel)
    escribir(DESTINO / "widgets" / "background.svg", emergente)
    escribir(DESTINO / "dialogs" / "background.svg", emergente)
    escribir(DESTINO / "solid" / "widgets" / "background.svg", svg_marco(24, 20, 12, 12, 24, 12, 24, 1, solido=True, sombra="anillo"))
    escribir(DESTINO / "solid" / "dialogs" / "background.svg", svg_marco(24, 20, 12, 12, 24, 12, 24, 1, solido=True, sombra="anillo"))
    escribir(DESTINO / "LEEME.txt",
             "OweeKoi Onda: estilo de Plasma propio de Owee (GPL-3.0). Lo que no define lo toma el tema por defecto.\n")
    print(f"plasma/desktoptheme/OweeKoi-Onda  ({sum(1 for _ in DESTINO.rglob('*.svg'))} svg)")
