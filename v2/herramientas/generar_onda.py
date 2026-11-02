#!/usr/bin/env python3
"""Decorado de ventanas propio de OweeKoi 2: "Onda" (Aurorae, claro y oscuro).

Dibujo original, sin partir de ningun otro tema. Solo se respeta el formato que exige Aurorae
(nombres de elementos y rejilla de 9 piezas). El rasgo propio de OweeKoi:
  - Doble linea de onda: un borde fino y, 3 px dentro, otro mas tenue, como un anillo de agua.
  - Botones en forma de escama de koi: circulo con un anillo interior; al pasar el raton
    aparece un anillo de onda alrededor.
  - Colores pastel de la paleta (paleta.py), sin rojo, amarillo ni verde saturados.

Un solo marco virtual se dibuja una vez y las 9 piezas (activa, inactiva y mascara) son
recortes de el, asi nunca desencajan. Salida: v2/ventanas/OweeKoi-Onda-{Dark,Light}/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paleta import CLARO, OSCURO, a_rgb  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent / "ventanas"

# --- geometria (px) ---------------------------------------------------------------------------
SH_T, SH_L, SH_R, SH_B = 20, 40, 40, 60    # extension de la sombra por lado
R = 12                                      # radio de las esquinas
TITULO = 31                                 # alto de la barra de titulo
CHIN = 12                                   # borde inferior: ahi se dibujan las esquinas de abajo
COL = (70, 145, 70)                         # ancho de las columnas (izquierda, centro, derecha)
FIL = (51, 86, CHIN + SH_B)                 # alto de las filas (arriba, centro, abajo)
FW, FH = sum(COL), sum(FIL)                 # marco virtual 285 x 209
CUERPO = (SH_L, SH_T, FW - SH_R, FH - SH_B)  # x0, y0, x1, y1 del cuerpo de la ventana
ORIGENES = {"activa": 35, "inactiva": 400, "mascara": 794}   # x de cada juego en el lienzo
Y0 = 59                                     # y de la primera fila


def hexa(h):
    return h


def mezclar(a, b, t):
    ca, cb = a_rgb(a), a_rgb(b)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


def a_rgba(h, alfa=1.0):
    r, g, b = a_rgb(h)
    return (r, g, b, round(alfa * 255))


def marco(modo, estado):
    """Marco completo como imagen RGBA (a SC veces el tamano). QtSvg ignora clipPath, asi que las
    piezas se entregan como imagenes del tamano exacto, no como recortes vectoriales."""
    import io  # noqa: F401
    from PIL import Image, ImageDraw, ImageFilter
    SC, SS = 2, 4                                   # escala de salida y supersampling
    k = SC * SS
    x0, y0, x1, y1 = (v * k for v in CUERPO)
    r = R * k
    lienzo = Image.new("RGBA", (FW * k, FH * k), (0, 0, 0, 0))
    if estado == "mascara":
        ImageDraw.Draw(lienzo).rounded_rectangle([x0, y0, x1 - 1, y1 - 1], r, fill=(0, 0, 0, 255))
        return lienzo.resize((FW * SC, FH * SC), Image.LANCZOS)

    P = OSCURO if modo == "dark" else CLARO
    activa = estado == "activa"
    fondo = P["superficie"] if activa else P["base"]
    if modo == "dark":
        linea = mezclar(fondo, P["texto"], 0.20 if activa else 0.12)
        onda, onda_a = P["texto"], 0.075 if activa else 0.04
        sombra, a0 = "#000000", 0.55 if activa else 0.34
    else:
        linea = mezclar(fondo, "#000000", 0.20 if activa else 0.11)
        onda, onda_a = "#ffffff", 0.60 if activa else 0.40
        sombra, a0 = "#1c2a24", 0.30 if activa else 0.17

    # sombra: cuerpo desenfocado y desplazado hacia abajo
    mascara = Image.new("L", lienzo.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle([x0, y0 + 9 * k, x1 - 1, y1 - 1 + 9 * k], r, fill=255)
    mascara = mascara.filter(ImageFilter.GaussianBlur(11 * k))
    mascara = mascara.point(lambda v: round(v * a0))
    capa = Image.new("RGBA", lienzo.size, a_rgba(sombra))
    capa.putalpha(mascara)
    lienzo = Image.alpha_composite(lienzo, capa)

    def dibujar(**kw):
        c = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
        ImageDraw.Draw(c).rounded_rectangle(**kw)
        return c

    lienzo = Image.alpha_composite(lienzo, dibujar(xy=[x0, y0, x1 - 1, y1 - 1], radius=r, fill=a_rgba(fondo)))
    inset = round(3.5 * k)
    lienzo = Image.alpha_composite(lienzo, dibujar(
        xy=[x0 + inset, y0 + inset, x1 - 1 - inset, y1 - 1 - inset], radius=r - inset,
        outline=a_rgba(onda, onda_a), width=k))
    lienzo = Image.alpha_composite(lienzo, dibujar(
        xy=[x0, y0, x1 - 1, y1 - 1], radius=r, outline=a_rgba(linea), width=k))
    return lienzo.resize((FW * SC, FH * SC), Image.LANCZOS)


def piezas(modo):
    """Las 9 piezas de cada juego, cada una una imagen PNG incrustada de su tamano exacto."""
    import base64
    import io
    SC = 2
    nombres = [["topleft", "top", "topright"], ["left", "center", "right"],
               ["bottomleft", "bottom", "bottomright"]]
    salida = []
    for estado, ox in ORIGENES.items():
        img = marco(modo, estado)
        prefijo = {"activa": "decoration", "inactiva": "decoration-inactive", "mascara": "mask"}[estado]
        fy = 0
        for f in range(3):
            fx = 0
            for c in range(3):
                w, h = COL[c], FIL[f]
                trozo = img.crop((fx * SC, fy * SC, (fx + w) * SC, (fy + h) * SC))
                buf = io.BytesIO()
                trozo.save(buf, "PNG", optimize=True)
                datos = base64.b64encode(buf.getvalue()).decode()
                gx, gy = ox + sum(COL[:c]), Y0 + sum(FIL[:f])
                salida.append(
                    f'<image id="{prefijo}-{nombres[f][c]}" x="{gx}" y="{gy}" width="{w}" height="{h}" '
                    f'preserveAspectRatio="none" xlink:href="data:image/png;base64,{datos}"/>')
                fx += w
            fy += FIL[f]
    return "".join(salida)


def decoracion(modo):
    ox = ORIGENES["activa"]
    pistas = [  # rectangulos que declaran margenes (solo importa su tamano)
        ("shadow-hint-top-margin", ox + 134, Y0, 4, SH_T), ("shadow-hint-bottom-margin", ox + 135, Y0 + 150, 4, SH_B),
        ("shadow-hint-left-margin", ox, Y0 + 75, SH_L, 4), ("shadow-hint-right-margin", ox + 245, Y0 + 81, SH_R, 4),
        ("hint-top-margin", ox + 146, Y0, 4, FIL[0]), ("hint-bottom-margin", ox + 147, Y0 + 137, 4, FIL[2]),
        ("hint-left-margin", ox, Y0 + 67, COL[0], 4), ("hint-right-margin", ox + 215, Y0 + 70, COL[2], 4),
    ]
    rects = "".join(f'<rect id="{i}" x="{x}" y="{y}" width="{w}" height="{h}" fill="#ff00ff"/>'
                    for i, x, y, w, h in pistas)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1100" height="310">'
            f'{piezas(modo)}{rects}</svg>')


# --- botones ------------------------------------------------------------------------------------
GLIFOS = {
    "close": '<path d="M5.4 5.4L10.6 10.6M10.6 5.4L5.4 10.6"/>',
    "minimize": '<path d="M5 8H11"/>',
    "maximize": '<path d="M6 10L10 6M7.2 6H10V8.8"/>',
    "restore": '<path d="M6 10L10 6M6 7.2V10H8.8"/>',
    "alldesktops": '<path d="M6.2 6.2h.01M9.8 6.2h.01M6.2 9.8h.01M9.8 9.8h.01" stroke-width="2.2"/>',
    "keepabove": '<path d="M5.8 9.6L8 7L10.2 9.6"/>',
    "keepbelow": '<path d="M5.8 6.4L8 9L10.2 6.4"/>',
}
COLORES = {  # (oscuro, claro)
    "close": ("#e08a78", "#d9705d"), "minimize": ("#e3bb70", "#d9ab4f"),
    "maximize": ("#8cc093", "#74ad7d"), "restore": ("#8cc093", "#74ad7d"),
    "alldesktops": ("#79b5ad", "#5f9d94"), "keepabove": ("#b7a3c9", "#9886aa"),
    "keepbelow": ("#b7a3c9", "#9886aa"),
}
ESTADOS = ["active", "inactive", "hover", "pressed", "deactivated", "hover-inactive",
           "deactivated-inactive"]


def boton(nombre, modo):
    c = COLORES[nombre][0 if modo == "dark" else 1]
    P = OSCURO if modo == "dark" else CLARO
    apagado = mezclar(P["elevado"], P["texto"], 0.12) if modo == "dark" else mezclar(P["base"], "#000000", 0.14)
    tinta = "#34261f"
    celdas = []
    for i, est in enumerate(ESTADOS):
        if est in ("inactive", "deactivated-inactive"):
            fondo, op = apagado, 1.0
        elif est == "deactivated":
            fondo, op = c, 0.45
        elif est == "hover-inactive":
            fondo, op = c, 0.75
        elif est == "pressed":
            fondo, op = mezclar(c, "#000000", 0.16), 1.0
        elif est == "hover":
            fondo, op = mezclar(c, "#ffffff", 0.10), 1.0
        else:
            fondo, op = c, 1.0
        anillo = mezclar(fondo, "#000000", 0.30)
        g = [f'<rect width="16" height="16" fill="#000" fill-opacity="0.004"/>',
             f'<circle cx="8" cy="8" r="6.6" fill="{fondo}" fill-opacity="{op}"/>',
             f'<circle cx="8" cy="8" r="4.1" fill="none" stroke="{anillo}" stroke-opacity="0.38" stroke-width="0.8"/>']
        if est in ("hover", "pressed", "hover-inactive"):
            g.append(f'<circle cx="8" cy="8" r="7.5" fill="none" stroke="{c}" stroke-opacity="0.55" stroke-width="0.7"/>')
            g.append(f'<g fill="none" stroke="{tinta}" stroke-opacity="0.8" stroke-width="1.3" '
                     f'stroke-linecap="round" stroke-linejoin="round">{GLIFOS[nombre]}</g>')
        celdas.append(f'<g id="{est}-center" transform="translate(0 {i * 16})">{"".join(g)}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="{16 * len(ESTADOS)}">'
            f'{"".join(celdas)}</svg>')


# --- configuracion y metadatos --------------------------------------------------------------------
def rgb(h):
    return ",".join(map(str, a_rgb(h)))


def rc(modo):
    P = OSCURO if modo == "dark" else CLARO
    return f"""[General]
ActiveFocusedTabColor={rgb(P['superficie'])}
ActiveUnfocusedTabColor={rgb(P['base'])}
InactiveFocusedTabColor={rgb(P['base'])}
InactiveUnfocusedTabColor={rgb(P['base'])}
ActiveTextColor={rgb(P['texto'])}
InactiveTextColor={rgb(P['suave'])}
TitleAlignment=Center
TitleVerticalAlignment=Center
UseTextShadow=false
LeftButtons=XIA
Shadow=true
Animation=1

[Layout]
BorderTop=0
BorderLeft=0
BorderRight=0
BorderBottom=0
TitleEdgeTop=8
TitleEdgeBottom=7
TitleEdgeLeft=16
TitleEdgeRight=16
TitleBorderLeft=50
TitleBorderRight=50
TitleHeight=16
ButtonWidth=16
ButtonHeight=16
ButtonSpacing=8
ButtonMarginTop=0
ButtonMarginLeft=0
ButtonMarginRight=0
ExplicitButtonSpacer=0
PaddingTop={SH_T}
PaddingBottom={CHIN + SH_B}
PaddingRight={SH_R}
PaddingLeft={SH_L}
TitleEdgeTopMaximized=8
TitleEdgeBottomMaximized=7
TitleEdgeLeftMaximized=16
TitleEdgeRightMaximized=16
"""


def metadatos(nombre, modo):
    json = f"""{{
    "KPackageStructure": "aurorae",
    "KPlugin": {{
        "Authors": [{{ "Name": "Owee" }}],
        "Category": "Plasma 6 Window Decorations",
        "ServiceTypes": ["aurorae"],
        "EnabledByDefault": true,
        "Name": "{nombre}",
        "Description": "Decorado de ventanas OweeKoi Onda ({'oscuro' if modo == 'dark' else 'claro'}): doble linea de onda y botones en forma de escama",
        "Id": "{nombre}",
        "License": "GPL-3.0+",
        "Version": "1.0",
        "X-KDE-PluginInfo-blur": false,
        "X-KPackage-Dependencies": []
    }}
}}
"""
    desktop = f"""[Desktop Entry]
Name={nombre}
X-KDE-PluginInfo-Author=Owee
X-KDE-PluginInfo-Name={nombre}
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-Category=
X-KDE-PluginInfo-Depends=
X-KDE-PluginInfo-License=GPL_V3
X-KDE-PluginInfo-EnabledByDefault=true
"""
    return json, desktop


def generar(modo):
    nombre = f"OweeKoi-Onda-{modo.capitalize()}"
    d = RAIZ / nombre
    d.mkdir(parents=True, exist_ok=True)
    (d / "decoration.svg").write_text(decoracion(modo), encoding="utf-8")
    for b in GLIFOS:
        (d / f"{b}.svg").write_text(boton(b, modo), encoding="utf-8")
    (d / f"{nombre}rc").write_text(rc(modo), encoding="utf-8")
    j, de = metadatos(nombre, modo)
    (d / "metadata.json").write_text(j, encoding="utf-8")
    (d / "metadata.desktop").write_text(de, encoding="utf-8")
    print(f"ventanas/{nombre}")


if __name__ == "__main__":
    generar("dark")
    generar("light")
