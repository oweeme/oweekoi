#!/usr/bin/env python3
"""Genera los temas globales de OweeKoi 2 (Plasma look-and-feel): OweeKoi Oscuro y OweeKoi Claro.

Al elegir uno en Configuracion del sistema > Temas globales se aplica TODO de una vez:
colores, iconos, estilo de Plasma, decorado de ventanas, punteros, pantalla de inicio, protector
del bloqueo, fondo de pantalla y animaciones. (El diseno de los paneles no se toca: es tuyo.)

Salida: v2/plasma/look-and-feel/org.owee.koi.{oscuro,claro}  (+ org.owee.koi, la pantalla de
inicio, que se copia sin cambios de la v1).
"""
import json
import shutil
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
L = RAIZ / "plasma" / "look-and-feel"
V1_SPLASH = RAIZ.parent / "tema" / "plasma" / "look-and-feel" / "org.owee.koi"

VARIANTES = {
    "oscuro": dict(esquema="OweeKoiDark", deco="Dark", nombre="Oscuro", estilo="tinta",
                   fondo="contents/images_dark"),
    "claro": dict(esquema="OweeKoiLight", deco="Light", nombre="Claro", estilo="papel",
                  fondo="contents/images"),
}

DEFAULTS = """[kcminputrc][Mouse]
cursorTheme=OweeKoi-Punteros

[kdeglobals][General]
ColorScheme={esquema}

[kdeglobals][Icons]
Theme=OweeKoi

[kdeglobals][KDE]
AnimationDurationFactor=1.2
widgetStyle=Breeze

[kscreenlockerrc][Greeter]
WallpaperPlugin=org.owee.koi

[ksplashrc][KSplash]
Theme=org.owee.koi

[kwinrc][Plugins]
magiclampEnabled=true
squashEnabled=false

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae
theme=__aurorae__svg__OweeKoi-Onda-{deco}

[plasmarc][Theme]
name=OweeKoi-Onda
"""

LAYOUT = """// OweeKoi: barra superior con el menu global y el reloj centrado. Sin dock.
// Plasma ejecuta esto al aplicar el tema; reconstruye siempre la misma disposicion.
var panel = new Panel;
panel.location = "top";
panel.height = 30;
panel.floating = true;
panel.hiding = "none";

var kickoff = panel.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["Shortcuts"];
kickoff.writeConfig("global", "Alt+F1");
panel.addWidget("org.kde.plasma.pager");
panel.addWidget("org.kde.plasma.appmenu");
panel.addWidget("org.kde.plasma.panelspacer");
panel.addWidget("org.kde.plasma.digitalclock");
panel.addWidget("org.kde.plasma.panelspacer");
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.showdesktop");

// Fondo: el del usuario si esta instalado ahi, si no el del sistema
var fondo = userDataPath("data") + "/wallpapers/OweeKoi-Estanque";
if (!fileExists(fondo)) { fondo = "/usr/share/wallpapers/OweeKoi-Estanque"; }
var escritorios = desktopsForActivity(currentActivity());
for (var i = 0; i < escritorios.length; i++) {
    escritorios[i].wallpaperPlugin = "org.kde.image";
    escritorios[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    escritorios[i].writeConfig("Image", "file://" + fondo);
}
"""

if __name__ == "__main__":
    L.mkdir(parents=True, exist_ok=True)
    if (L / "org.owee.koi").exists():
        shutil.rmtree(L / "org.owee.koi")
    shutil.copytree(V1_SPLASH, L / "org.owee.koi")
    for clave, v in VARIANTES.items():
        d = L / f"org.owee.koi.{clave}"
        if d.exists():
            shutil.rmtree(d)
        (d / "contents" / "previews").mkdir(parents=True)
        meta = {"KPackageStructure": "Plasma/LookAndFeel", "KPlugin": {
            "Authors": [{"Name": "Owee"}],
            "Description": f"OweeKoi 2 en modo {v['estilo']}: colores, iconos, estilo de Plasma, ventanas con ondas, "
                           "punteros, fondo, protector, pantalla de inicio y animaciones",
            "Id": f"org.owee.koi.{clave}", "License": "GPL-3.0+", "Name": f"OweeKoi {v['nombre']}",
            "Version": "2.0"}}
        (d / "metadata.json").write_text(json.dumps(meta, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        (d / "contents" / "defaults").write_text(DEFAULTS.format(**v), encoding="utf-8")
        (d / "contents" / "layouts").mkdir()
        (d / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js").write_text(LAYOUT, encoding="utf-8")
        im = Image.open(RAIZ / "fondos" / "OweeKoi-Estanque" / v["fondo"] / "2560x1440.jpg").convert("RGB")
        im.resize((640, 360), Image.LANCZOS).save(d / "contents" / "previews" / "preview.png")
    print("temas globales:", sorted(p.name for p in L.iterdir()))
