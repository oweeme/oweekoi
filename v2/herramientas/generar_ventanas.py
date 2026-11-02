#!/usr/bin/env python3
"""Genera el decorado de ventanas (Aurorae) y el estilo de Plasma de OweeKoi 2.

Parte de WhiteSur (vinceliuice, GPL-3.0) ya instalado en tu equipo y lo recolorea con la
paleta de OweeKoi; no se redistribuye el original. Los derivados siguen siendo GPL-3.0 y
conservan el credito a WhiteSur.

Salida (dentro de v2/):
  ventanas/OweeKoi-Dark, ventanas/OweeKoi-Light   decorado Aurorae: barra de titulo en tinta o
                                                  papel y botones en pastel, sin colores chillones
  plasma/desktoptheme/OweeKoi                     estilo de Plasma sin archivo de colores, para que
                                                  siga el esquema activo (claro u oscuro)
"""
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paleta import CLARO, OSCURO, a_rgb  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOME = Path.home()
WS_AURORAE = HOME / ".local/share/aurorae/themes/WhiteSur-dark"
WS_PLASMA = HOME / ".local/share/plasma/desktoptheme/WhiteSur-dark"

# Barra de titulo de WhiteSur (de la mas clara a la mas oscura) -> colores de la paleta
GRISES = {"#363636": "superficie", "#2d2d2d": "base", "#242424": "vista", "#1a1a1a": "vista"}
GRISES_CLARO = {"#363636": "#e4dfce", "#2d2d2d": "#ece7d8", "#242424": "#f2eee2", "#1a1a1a": "#f7f3e8"}

# Botones: de saturados a pastel. cierre=coral, minimizar=ambar, maximizar=verde de seleccion.
BOTONES = {
    "dark": {"#e9524a": "#e08a78", "#f1ae1b": "#e3bb70", "#59c837": "#8cc093"},
    "light": {"#e9524a": "#d9705d", "#f1ae1b": "#d9ab4f", "#59c837": "#74ad7d"},
}
# Otros botones (siempre arriba / en todos los escritorios) en tonos mas apagados
SUAVIZAR = {"#c5a8ce": "#b7a3c9", "#bfa2c8": "#ab98bd", "#d1b6da": "#c2b0d1", "#ccb0d5": "#bba8cb",
            "#ab90b4": "#9886aa", "#9e83a7": "#8c7a9d",
            "#70c4bb": "#79b5ad", "#58b4aa": "#64a198", "#8cd6d2": "#8fc4be", "#3d9388": "#4f8279",
            "#7dd1c8": "#86bdb6"}


def sustituir(texto, mapa):
    for viejo, nuevo in mapa.items():
        texto = re.sub(re.escape(viejo), nuevo, texto, flags=re.I)
    return texto


def rgb(h):
    return ",".join(map(str, a_rgb(h)))


def aurorae(modo):
    P = OSCURO if modo == "dark" else CLARO
    destino = RAIZ / "ventanas" / f"OweeKoi-{modo.capitalize()}"
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(WS_AURORAE, destino)
    (destino / "WhiteSur-darkrc").rename(destino / f"OweeKoi-{modo.capitalize()}rc")
    nombre = f"OweeKoi-{modo.capitalize()}"

    grises = ({k: P[v] for k, v in GRISES.items()} if modo == "dark" else GRISES_CLARO)
    mapa_botones = {**BOTONES[modo], **SUAVIZAR}
    for svg in destino.glob("*.svg"):
        t = svg.read_text(encoding="utf-8")
        t = sustituir(t, grises) if svg.name == "decoration.svg" else sustituir(t, mapa_botones)
        svg.write_text(t, encoding="utf-8")

    rc = destino / f"{nombre}rc"
    t = rc.read_text(encoding="utf-8")
    colores = {
        "ActiveFocusedTabColor": P["superficie"], "ActiveUnfocusedTabColor": P["base"],
        "InactiveFocusedTabColor": P["base"], "InactiveUnfocusedTabColor": P["base"],
        "ActiveTextColor": P["texto"], "InactiveTextColor": P["suave"],
    }
    for clave, valor in colores.items():
        t = re.sub(rf"^{clave}=.*$", f"{clave}={rgb(valor)}", t, flags=re.M)
    # sin sombra de texto blanca: en papel y en tinta mancha el texto
    t = re.sub(r"^UseTextShadow=.*$", "UseTextShadow=false", t, flags=re.M)
    rc.write_text(t, encoding="utf-8")

    for meta in ("metadata.json", "metadata.desktop"):
        f = destino / meta
        if f.exists():
            f.write_text(f.read_text(encoding="utf-8").replace("WhiteSur-dark", nombre)
                         .replace("WhiteSur", "OweeKoi"), encoding="utf-8")
    (destino / "LEEME.txt").write_text(
        "Derivado de WhiteSur (vinceliuice), GPL-3.0. Recoloreado con la paleta de OweeKoi.\n",
        encoding="utf-8")
    print(f"ventanas/{nombre}")


def plasma():
    destino = RAIZ / "plasma" / "desktoptheme" / "OweeKoi"
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(WS_PLASMA, destino)
    # sin 'colors' el tema usa el esquema de color activo (OweeKoiDark u OweeKoiLight)
    (destino / "colors").unlink(missing_ok=True)
    for meta in ("metadata.json", "metadata.desktop"):
        f = destino / meta
        if f.exists():
            t = f.read_text(encoding="utf-8")
            t = t.replace("WhiteSur-dark", "OweeKoi").replace("WhiteSur", "OweeKoi")
            f.write_text(t, encoding="utf-8")
    (destino / "LEEME.txt").write_text(
        "Derivado de WhiteSur (vinceliuice), GPL-3.0. Sin archivo de colores: sigue el esquema activo.\n",
        encoding="utf-8")
    print("plasma/desktoptheme/OweeKoi")


if __name__ == "__main__":
    for requisito in (WS_AURORAE, WS_PLASMA):
        if not requisito.exists():
            sys.exit(f"Falta {requisito} (instala WhiteSur con el instalador de OweeKoi)")
    aurorae("dark")
    aurorae("light")
    plasma()
