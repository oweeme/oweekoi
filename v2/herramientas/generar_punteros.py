#!/usr/bin/env python3
"""Punteros propios de OweeKoi 2 (tema de cursores Xcursor).

Dibujo original; solo se redibujan las formas que definen el estilo y el resto se hereda de
Breeze (el cursor de texto, los de redimensionar, etc.), asi que el tema siempre esta completo.

  default    flecha en crema con contorno de tinta y sombra suave
  pointer    la misma flecha con un anillo de onda en la punta ("se puede pulsar")
  wait       el logo de Owee con ondas que se expanden (cargando)
  progress   la flecha con un logo pequeno y ondas en la esquina (trabajando en segundo plano)

Salida: v2/punteros/OweeKoi-Punteros/{index.theme,cursors/}. Necesita xcursorgen y Pillow.
"""
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "punteros" / "OweeKoi-Punteros"
LOGO = RAIZ.parent / "tema" / "iconos" / "256" / "oweelogo.png"
TAMANOS = (24, 32, 48, 64)
SS = 8  # supersampling

CREMA, TINTA, CORAL = (246, 241, 225), (45, 42, 44), (242, 117, 95)

# Puntos de la flecha (x, y) con la punta en (0, 0) y alto 1
FLECHA = [(0, 0), (0, 0.80), (0.19, 0.63), (0.33, 0.97), (0.47, 0.91), (0.34, 0.58), (0.58, 0.58)]

# Alias por compatibilidad (los mismos nombres que usa Breeze)
ALIAS = {
    "default": ["left_ptr", "arrow", "top_left_arrow", "left_arrow"],
    "pointer": ["hand1", "hand2", "pointing_hand", "9d800788f1b08800ae810202380a0822",
                "e29285e634086352946a0e7090d73106"],
    "wait": ["watch", "0426c94ea35c87780ff01dc239897213"],
    "progress": ["left_ptr_watch", "half-busy", "00000000000000020006000e7e9ffc3f",
                 "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"],
}


def lienzo(s):
    return Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))


def con_sombra(capa, s, dx=0.035, dy=0.055, difum=0.035, alfa=0.38):
    """Devuelve la capa con su sombra suave debajo."""
    a = capa.getchannel("A")
    desplazada = Image.new("L", a.size, 0)     # paste y no offset: offset "enrolla" el borde
    desplazada.paste(a, (int(dx * s * SS), int(dy * s * SS)))
    a = desplazada.filter(ImageFilter.GaussianBlur(difum * s * SS))
    sombra = Image.new("RGBA", capa.size, (30, 28, 30, 0))
    sombra.putalpha(a.point(lambda v: round(v * alfa)))
    return Image.alpha_composite(sombra, capa)


def flecha(capa, s, x, y, alto):
    """Dibuja la flecha con la punta en (x, y) (en px finales) y el alto dado."""
    k = alto * SS
    pts = [((x * SS + px * k), (y * SS + py * k)) for px, py in FLECHA]
    d = ImageDraw.Draw(capa)
    grosor = max(2, round(0.085 * alto * SS))
    d.polygon(pts, fill=CREMA + (255,))
    d.line(pts + [pts[0]], fill=TINTA + (255,), width=grosor, joint="curve")
    for p in pts:  # esquinas redondeadas
        d.ellipse([p[0] - grosor / 2, p[1] - grosor / 2, p[0] + grosor / 2, p[1] + grosor / 2], fill=TINTA + (255,))


def anillo(capa, cx, cy, r, ancho, color, alfa):
    d = ImageDraw.Draw(capa)
    ov = Image.new("RGBA", capa.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], outline=color + (round(255 * alfa),), width=max(1, round(ancho)))
    capa.alpha_composite(ov)


def logo(capa, cx, cy, diametro):
    im = Image.open(LOGO).convert("RGBA").resize((round(diametro), round(diametro)), Image.LANCZOS)
    sombra = im.getchannel("A").filter(ImageFilter.GaussianBlur(diametro * 0.05))
    sh = Image.new("RGBA", im.size, (30, 28, 30, 0))
    sh.putalpha(sombra.point(lambda v: round(v * 0.35)))
    capa.alpha_composite(sh, (round(cx - diametro / 2), round(cy - diametro / 2 + diametro * 0.05)))
    capa.alpha_composite(im, (round(cx - diametro / 2), round(cy - diametro / 2)))


def fin(capa, s):
    return capa.resize((s, s), Image.LANCZOS)


# --- cada puntero devuelve una lista de fotogramas [(imagen, xhot, yhot, retardo_ms)] ------------
def dibujar_default(s):
    m = 0.07 * s
    c = lienzo(s)
    flecha(c, s, m, m, 0.80 * s)
    return [(fin(con_sombra(c, s), s), round(m), round(m), 0)]


def dibujar_pointer(s):
    m = 0.30 * s
    c = lienzo(s)                      # anillos debajo, sin sombra
    anillo(c, m * SS, m * SS, 0.26 * s * SS, 0.045 * s * SS, CORAL, 0.45)
    anillo(c, m * SS, m * SS, 0.17 * s * SS, 0.055 * s * SS, CORAL, 0.95)
    f = lienzo(s)                      # la flecha lleva su propia sombra
    flecha(f, s, m, m, 0.68 * s)
    c.alpha_composite(con_sombra(f, s))
    return [(fin(c, s), round(m), round(m), 0)]


def ondas(c, cx, cy, r_ini, r_fin, ancho, t):
    """Dos anillos que se expanden y se desvanecen; t en [0, 1)."""
    for desfase in (0.0, 0.5):
        u = (t + desfase) % 1.0
        r = r_ini + (r_fin - r_ini) * u
        anillo(c, cx, cy, r, ancho, CORAL, 0.9 * (1 - u) ** 1.4)


def dibujar_wait(s, n=24):
    out = []
    for i in range(n):
        c = lienzo(s)
        t = i / n
        ondas(c, s * SS / 2, s * SS / 2, 0.30 * s * SS, 0.50 * s * SS, 0.055 * s * SS, t)
        pulso = 1 + 0.03 * math.sin(2 * math.pi * t)  # el logo "respira" muy poco
        logo(c, s * SS / 2, s * SS / 2, 0.56 * s * SS * pulso)
        out.append((fin(c, s), s // 2, s // 2, 50))
    return out


def dibujar_progress(s, n=24):
    m = 0.07 * s
    out = []
    for i in range(n):
        c = lienzo(s)
        t = i / n
        flecha(c, s, m, m, 0.62 * s)
        c = con_sombra(c, s, alfa=0.30)
        cx, cy = 0.70 * s * SS, 0.70 * s * SS
        ondas(c, cx, cy, 0.20 * s * SS, 0.30 * s * SS, 0.04 * s * SS, t)
        logo(c, cx, cy, 0.38 * s * SS)
        out.append((fin(c, s), round(m), round(m), 50))
    return out


DIBUJOS = {"default": dibujar_default, "pointer": dibujar_pointer, "wait": dibujar_wait,
           "progress": dibujar_progress}


def construir():
    if not shutil.which("xcursorgen"):
        sys.exit("Falta xcursorgen (paquete x11-apps / xcursorgen)")
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    cursores = SALIDA / "cursors"
    cursores.mkdir(parents=True)
    (SALIDA / "index.theme").write_text(
        "[Icon Theme]\nName=OweeKoi Punteros\nComment=Flecha crema con ondas y el logo de Owee al cargar\n"
        "Inherits=breeze_cursors\n", encoding="utf-8")
    (SALIDA / "cursor.theme").write_text("[Icon Theme]\nInherits=OweeKoi-Punteros\n", encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for nombre, f in DIBUJOS.items():
            lineas = []
            for s in TAMANOS:
                for i, (img, xh, yh, retardo) in enumerate(f(s)):
                    archivo = f"{nombre}-{s}-{i:02d}.png"
                    img.save(tmp / archivo)
                    lineas.append(f"{s} {xh} {yh} {archivo}" + (f" {retardo}" if retardo else ""))
            (tmp / f"{nombre}.cfg").write_text("\n".join(lineas) + "\n")
            subprocess.run(["xcursorgen", f"{nombre}.cfg", str(cursores / nombre)], cwd=tmp, check=True)
    for destino, alias in ALIAS.items():
        for a in alias:
            (cursores / a).symlink_to(destino)
    print(f"{len(list(cursores.iterdir()))} entradas en {cursores}")


if __name__ == "__main__":
    construir()
