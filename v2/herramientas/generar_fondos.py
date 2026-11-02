#!/usr/bin/env python3
"""Genera los fondos de OweeKoi 2: el estanque en modo tinta (oscuro) y papel (claro).

Salida:
  v2/fondos/OweeKoi-Estanque/        paquete de fondo de Plasma con par claro/oscuro
      contents/images/2560x1440.jpg        (modo claro)
      contents/images_dark/2560x1440.jpg   (modo oscuro; Plasma lo elige solo)
  v2/plasma/wallpapers/org.owee.koi/contents/images/agua-{claro,oscuro}.jpg
                                     agua sin peces: base del protector animado

Los kois salen de las hojas de sprites de OweeKoi 1 (tema/plasma/wallpapers/org.owee.koi).
Todo es procedural y con semilla fija: el mismo comando da siempre la misma imagen.
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
V1_IMG = RAIZ.parent / "tema" / "plasma" / "wallpapers" / "org.owee.koi" / "contents" / "images"
PAQUETE = RAIZ / "fondos" / "OweeKoi-Estanque"
PLUGIN_IMG = RAIZ / "plasma" / "wallpapers" / "org.owee.koi" / "contents" / "images"

W, H = 2560, 1440
SS = 2  # supersampling para lineas finas

# Colores por modo. Oscuro = tinta (agua profunda y apagada); claro = papel (agua celadon suave).
MODOS = {
    "oscuro": dict(centro=(37, 55, 51), borde=(19, 28, 27), nube=(255, 255, 255, 9),
                   onda=(236, 230, 214, 34), hoja=(76, 122, 96), vena=(40, 70, 56),
                   luz=(104, 152, 124), sombra=(0, 0, 0, 120)),
    "claro": dict(centro=(196, 218, 203), borde=(160, 188, 170), nube=(255, 255, 255, 38),
                  onda=(255, 255, 255, 120), hoja=(120, 170, 134), vena=(82, 128, 98),
                  luz=(158, 202, 168), sombra=(30, 60, 45, 70)),
}

# Ondas (x, y, radio) en fraccion de pantalla; hojas (x, y, radio, giro)
ONDAS = [(0.27, 0.30, 0.16), (0.56, 0.74, 0.13), (0.80, 0.42, 0.09), (0.12, 0.72, 0.07)]
HOJAS = [(0.09, 0.82, 0.062, 20), (0.89, 0.15, 0.052, 140), (0.93, 0.80, 0.036, 260),
         (0.17, 0.12, 0.034, 80), (0.60, 0.92, 0.028, 200)]

# Kois del fondo fijo: hoja, fotograma, centro (fraccion), rumbo (grados, 0=derecha), escala
KOIS = [
    ("koi-kohaku.png", 7, (0.40, 0.44), 205, 0.92),
    ("koi-showa.png", 7, (0.64, 0.58), 25, 0.86),
    ("koi-ogon.png", 3, (0.80, 0.25), 150, 0.50),
]
FRAME_W = 876


def agua(modo, semilla=7):
    c = MODOS[modo]
    rng = np.random.default_rng(semilla)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # gradiente radial con el centro un poco desplazado
    d = np.sqrt(((x - W * 0.52) / (W * 0.62)) ** 2 + ((y - H * 0.46) / (H * 0.74)) ** 2)
    t = np.clip(d, 0, 1)[..., None] ** 1.35
    centro, borde = np.array(c["centro"], np.float32), np.array(c["borde"], np.float32)
    base = centro * (1 - t) + borde * t
    # nubes de luz muy suaves (baja frecuencia)
    for escala, fuerza in ((260, 7.0), (110, 3.5)):
        ruido = rng.random((H // escala + 3, W // escala + 3)).astype(np.float32)
        ruido = np.array(Image.fromarray((ruido * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC),
                         np.float32)
        base += ((ruido / 255.0 - 0.5) * fuerza)[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

    # todo lo fino se dibuja al doble de tamano y se reduce
    capa = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dib = ImageDraw.Draw(capa)
    for fx, fy, fr in ONDAS:
        for i, k in enumerate((1.0, 0.72, 0.46, 0.24)):
            r = fr * H * SS * k
            a = int(c["onda"][3] * (1 - i * 0.2))
            dib.ellipse([fx * W * SS - r * 1.18, fy * H * SS - r, fx * W * SS + r * 1.18, fy * H * SS + r],
                        outline=(*c["onda"][:3], a), width=2 * SS)
    capa = capa.resize((W, H), Image.LANCZOS)
    img = Image.alpha_composite(img, capa)

    rnd = random.Random(semilla)
    for fx, fy, fr, giro in HOJAS:
        img = hoja_de_loto(img, fx * W, fy * H, fr * H, giro, c, rnd)
    # nube clara encima (da profundidad al agua)
    velo = Image.new("RGBA", (W, H), c["nube"])
    velo.putalpha(Image.fromarray((np.clip(1 - t[..., 0], 0, 1) * c["nube"][3]).astype(np.uint8)))
    return Image.alpha_composite(img, velo).convert("RGB")


def hoja_de_loto(img, cx, cy, r, giro, c, rnd):
    n = 72
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        radio = r * (1 + 0.035 * math.sin(a * 3 + rnd.random()) + 0.02 * rnd.uniform(-1, 1))
        pts.append((cx + radio * math.cos(a), cy + radio * math.sin(a)))
    # muesca en V, como las hojas reales
    muesca = math.radians(giro)
    pts2 = [(cx + math.cos(muesca) * 0, cy + math.sin(muesca) * 0)]
    for (px, py), i in zip(pts, range(n)):
        a = (2 * math.pi * i / n - muesca + math.pi) % (2 * math.pi) - math.pi
        if abs(a) > 0.11:
            pts2.append((px, py))
    forma = Image.new("L", img.size, 0)
    ImageDraw.Draw(forma).polygon(pts2, fill=255)
    # sombra
    sombra = forma.filter(ImageFilter.GaussianBlur(r * 0.07))
    sombra = ImageChops.offset(sombra, int(r * 0.09), int(r * 0.12))
    capa_s = Image.new("RGBA", img.size, c["sombra"])
    capa_s.putalpha(sombra.point(lambda v: v * c["sombra"][3] // 255))
    img = Image.alpha_composite(img, capa_s)
    # cuerpo con un leve degradado
    cuerpo = Image.new("RGBA", img.size, (*c["hoja"], 255))
    luz = Image.new("RGBA", img.size, (*c["luz"], 255))
    mascara_luz = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara_luz).ellipse([cx - r * 0.9, cy - r * 1.0, cx + r * 0.3, cy + r * 0.2], fill=110)
    mascara_luz = mascara_luz.filter(ImageFilter.GaussianBlur(r * 0.35))
    cuerpo = Image.composite(luz, cuerpo, mascara_luz)
    cuerpo.putalpha(forma)
    img = Image.alpha_composite(img, cuerpo)
    # venas
    dib = ImageDraw.Draw(img)
    for k in range(9):
        a = muesca + math.radians(14) + k * (2 * math.pi - math.radians(28)) / 8
        dib.line([(cx, cy), (cx + r * 0.94 * math.cos(a), cy + r * 0.94 * math.sin(a))],
                 fill=(*c["vena"], 150), width=max(1, int(r * 0.012)))
    return img


def koi(hoja, cuadro, escala):
    hoja_img = Image.open(V1_IMG / hoja).convert("RGBA")
    fw, fh = hoja_img.size[0] // 4, hoja_img.size[1] // 4
    col, fila = cuadro % 4, cuadro // 4
    f = hoja_img.crop((col * fw, fila * fh, (col + 1) * fw, (fila + 1) * fh))
    # el cuerpo mide ~650 px dentro del cuadro de 876; a escala 1 queda en ~900 px de 2560
    k = escala * 1.38 * W / 2560
    return f.resize((int(f.size[0] * k), int(f.size[1] * k)), Image.LANCZOS)


def con_kois(fondo):
    img = fondo.convert("RGBA")
    for hoja, cuadro, (fx, fy), rumbo, escala in KOIS:
        pez = koi(hoja, cuadro, escala)
        pez = pez.rotate(rumbo - 180, expand=True, resample=Image.BICUBIC)  # el pez mira a 180 grados
        img.alpha_composite(pez, (int(fx * W - pez.size[0] / 2), int(fy * H - pez.size[1] / 2)))
    return img.convert("RGB")


def guardar(img, ruta, calidad=92):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    img.save(ruta, "JPEG", quality=calidad, optimize=True, progressive=True)
    print(f"{ruta.relative_to(RAIZ)}  {ruta.stat().st_size // 1024} KB")


if __name__ == "__main__":
    fondos = {m: agua(m) for m in MODOS}
    # base animada (sin peces)
    for m, img in fondos.items():
        guardar(img, PLUGIN_IMG / f"agua-{m}.jpg", 90)
    # fondos fijos con kois: claro e oscuro
    guardar(con_kois(fondos["claro"]), PAQUETE / "contents" / "images" / "2560x1440.jpg")
    guardar(con_kois(fondos["oscuro"]), PAQUETE / "contents" / "images_dark" / "2560x1440.jpg")
    prev = con_kois(fondos["oscuro"]).resize((400, 225), Image.LANCZOS)
    guardar(prev, PAQUETE / "contents" / "screenshot.jpg", 88)
