#!/usr/bin/env python3
"""Genera el tema de iconos OweeKoi (carpetas de colores) desde paleta.py.

Estilo mate y suave, pensado para no cansar la vista: sin brillos ni reflejos, colores
pastel con poca saturacion y un simbolo grabado (mas oscuro que la carpeta) para reconocer
cada una. Un solo juego sirve para modo claro y oscuro.

Salida: v2/iconos/OweeKoi/ (index.theme + places/scalable/*.svg). El tema hereda de OweeLogo,
WhiteSur-dark, breeze y hicolor: solo reemplaza las carpetas, el resto de iconos sigue igual.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paleta import CARPETAS, color_carpeta  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent / "iconos" / "OweeKoi"
SALIDA = RAIZ / "places" / "scalable"

PLANTILLA = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="frente" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{claro}"/>
      <stop offset="1" stop-color="{base}"/>
    </linearGradient>
  </defs>
  <path d="M8 14a4 4 0 0 1 4-4h12.6a4 4 0 0 1 2.9 1.2l2.6 2.8H52a4 4 0 0 1 4 4v8H8z" fill="{atras}"/>
  <rect x="6" y="19" width="52" height="35" rx="5" fill="url(#frente)"/>
  <rect x="6" y="19" width="52" height="35" rx="5" fill="none" stroke="{borde}" stroke-opacity=".25"/>
  <g fill="none" stroke="{simbolo}" stroke-opacity=".62" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{glifo}</g>
</svg>
"""

# Simbolos grabados dentro de la carpeta (viewBox 64; la hoja frontal ocupa y=19..54)
GLIFOS = {
    "": "",
    "documento": '<rect x="25" y="28" width="14" height="18" rx="2"/><path d="M28.5 34h7M28.5 38h7M28.5 42h4" stroke-width="1.8"/>',
    "descarga": '<path d="M32 29v13M26.5 36.5 32 42l5.5-5.5M26 47h12" stroke-width="2.2"/>',
    "musica": '<path d="M37 28v13M37 28q4.5 1 5 6"/><ellipse cx="33" cy="42" rx="4" ry="3" fill="currentColor" stroke="none"/>',
    "imagen": '<rect x="24" y="28" width="16" height="16" rx="2"/><path d="M25 41l5-5 4 4 3-3 3 3.5" stroke-width="1.8"/><circle cx="35.5" cy="33" r="1.6" fill="currentColor" stroke="none"/>',
    "video": '<rect x="23" y="29" width="18" height="15" rx="3"/><path d="M30 33v7l6-3.5z" fill="currentColor"/>',
    "escritorio": '<rect x="23" y="28" width="18" height="12" rx="1.8"/><path d="M32 40v5M27.5 45.5h9"/>',
    "plantillas": '<rect x="25.5" y="29" width="5.5" height="5.5" rx="1.2"/><rect x="33" y="29" width="5.5" height="5.5" rx="1.2"/><rect x="25.5" y="36.5" width="5.5" height="5.5" rx="1.2"/><rect x="33" y="36.5" width="5.5" height="5.5" rx="1.2"/>',
    "compartida": '<circle cx="28" cy="33.5" r="3"/><circle cx="37" cy="33.5" r="3"/><path d="M22 46q6-9 12 0M31 46q6-9 12 0" stroke-width="1.8"/>',
}

# Nombre del icono -> (color, simbolo). Los nombres son los que usan Dolphin y KDE.
USO = {
    "folder": ("azul", ""),
    "folder-documents": ("azul", "documento"),
    "folder-download": ("verde", "descarga"),
    "folder-music": ("rosa", "musica"),
    "folder-pictures": ("naranja", "imagen"),
    "folder-videos": ("violeta", "video"),
    "user-desktop": ("turquesa", "escritorio"),
    "folder-templates": ("gris", "plantillas"),
    "folder-publicshare": ("gris", "compartida"),
    "folder-open": ("azul", ""),
    "inode-directory": ("azul", ""),
}

# Carpetas "por nombre": KDE busca folder-<nombre> segun como se llame la carpeta (Android,
# Dev...) o el icono que alguien eligio en su .directory. Se cubren todos los nombres que usan
# WhiteSur y Breeze para que ninguno caiga a un icono de otro estilo o a uno generico.
GLIFOS.update({
    "codigo": '<path d="M28 33l-5 5 5 5M36 33l5 5-5 5M33.5 31l-3 14" stroke-width="1.9"/>',
    "android": '<path d="M24.5 42a7.5 7.5 0 0 1 15 0z"/><path d="M27 34l-2-3M37 34l2-3"/><circle cx="29.2" cy="39" r=".9" fill="currentColor" stroke="none"/><circle cx="34.8" cy="39" r=".9" fill="currentColor" stroke="none"/>',
    "qt": '<rect x="23" y="28" width="18" height="18" rx="4.5"/><circle cx="32" cy="36.2" r="4"/><path d="M33.6 38.4l3.2 3.6"/>',
    "rama": '<circle cx="27" cy="31.5" r="2"/><circle cx="27" cy="45" r="2"/><circle cx="37.5" cy="36" r="2"/><path d="M27 33.5v9.5M27 41.5c0-4.5 10.5-2 10.5-3.5"/>',
})
GRUPOS = {
    # color: nombres (sin el prefijo folder-)
    "rojo": "red", "amarillo": "yellow",
    "verde": "green build development extension flatpak godot java library projects script snap "
             "steam vbox wine windows mac blender docker deb rpm appimage tar torrent games "
             "download-open downloads",
    "turquesa": "cyan desktop public publicshare network remote remote-ftp remote-nfs remote-smb "
                "remote-ssh remote-open cloud gdrive dropbox onedrive owncloud",
    "azul": "blue activities bookmarks bookmark book calculate chart comic database decrypted "
            "documents-open encrypted favorites home important language locked log mail notes "
            "open presentation print recent sign table text txt unlocked visiting html",
    "violeta": "violet magenta videos-open video videos videocamera",
    "rosa": "music music-open sound podcast",
    "gris": "publicshare-open black grey root temp trash crash templates-open drag-accept tab",
    "naranja": "orange brown camera design drawing image image-people images paint photo photos "
               "picture pictures-open",
}
# nombres que ademas llevan simbolo
SIMBOLOS = {"code": "codigo", "development": "codigo", "android": "android", "qt": "qt",
            "git": "rama", "github": "rama"}
EXTRA = {"android": "verde", "qt": "verde", "code": "verde", "git": "verde", "github": "verde"}

INDEX = """[Icon Theme]
Name=OweeKoi
Comment=Carpetas de colores suaves y mate de OweeKoi
Inherits=OweeLogo,WhiteSur-dark,breeze,hicolor
Directories=places/scalable

[places/scalable]
Size=64
MinSize=16
MaxSize=512
Type=Scalable
Context=Places
"""


def mezcla(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def svg(color, glifo=""):
    simbolo = mezcla(color, "#000000", 0.42)
    return PLANTILLA.format(
        base=color, claro=mezcla(color, "#ffffff", 0.07), atras=mezcla(color, "#000000", 0.24),
        borde=mezcla(color, "#000000", 0.55), simbolo=simbolo,
        glifo=GLIFOS[glifo].replace("currentColor", simbolo))


if __name__ == "__main__":
    if SALIDA.exists():
        shutil.rmtree(RAIZ)
    SALIDA.mkdir(parents=True)
    (RAIZ / "index.theme").write_text(INDEX, encoding="utf-8")
    # carpetas de colores lisas, para ponerselas a mano a una carpeta concreta
    for nombre in [*CARPETAS, "gris"]:
        (SALIDA / f"folder-owee-{nombre}.svg").write_text(svg(color_carpeta(nombre)), encoding="utf-8")
    # carpetas del sistema, cada una con su color y su simbolo
    for icono, (color, glifo) in USO.items():
        (SALIDA / f"{icono}.svg").write_text(svg(color_carpeta(color), glifo), encoding="utf-8")
    # el resto de nombres que KDE puede pedir (por carpeta o por .directory)
    for color, nombres in GRUPOS.items():
        for n in nombres.split():
            icono = f"folder-{n}"
            if icono in USO or (SALIDA / f"{icono}.svg").exists():
                continue
            (SALIDA / f"{icono}.svg").write_text(
                svg(color_carpeta(color), SIMBOLOS.get(n, "")), encoding="utf-8")
    for n, color in EXTRA.items():
        icono = f"folder-{n}"
        (SALIDA / f"{icono}.svg").write_text(
            svg(color_carpeta(color), SIMBOLOS.get(n, "")), encoding="utf-8")
    print(f"{len(list(SALIDA.glob('*.svg')))} iconos en {RAIZ}")
