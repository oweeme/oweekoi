#!/usr/bin/env python3
"""Temas de editor y terminal de OweeKoi 2: Konsole, Kate (KSyntaxHighlighting) y Qt Creator.

Parten de paleta.py. Cada color de sintaxis se comprueba contra el fondo del editor y, si no llega a
4.5:1 (WCAG AA), se acerca al color de texto hasta que se lea bien: nada se elige "a ojo".

Salida (dentro de v2/editores/):
  konsole/OweeKoi-{Oscuro,Claro}.colorscheme     -> ~/.local/share/konsole/
  kate/OweeKoi-{Oscuro,Claro}.theme              -> ~/.local/share/org.kde.syntax-highlighting/themes/
  qtcreator/OweeKoi-{Oscuro,Claro}.xml           -> ~/.config/QtProject/qtcreator/styles/
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paleta import CLARO, OSCURO, a_rgb, contraste  # noqa: E402

SALIDA = Path(__file__).resolve().parent.parent / "editores"


def mezclar(a, b, t):
    ca, cb = a_rgb(a), a_rgb(b)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


def legible(color, fondo, texto, minimo=4.5):
    """Acerca 'color' a 'texto' hasta llegar al contraste minimo contra 'fondo'."""
    t = 0.0
    while contraste(mezclar(color, texto, t), fondo) < minimo and t < 1:
        t += 0.05
    return mezclar(color, texto, t)


# Tonos de sintaxis por modo (se ajustan despues): nombre -> color base
SINTAXIS = {
    "oscuro": dict(palabra="#f08a76", funcion="#8cc093", tipo="#7cb9f0", cadena="#e8b65c", numero="#b5a8f0",
                   constante="#79b5ad", comentario="#8f887c", directiva="#d9a05f", error="#f58a76",
                   aviso="#e8b65c", info="#7cb9f0"),
    "claro": dict(palabra="#b53a26", funcion="#2b7a4b", tipo="#1d62a0", cadena="#8f5f00", numero="#6a54b8",
                  constante="#2f6f68", comentario="#7a736a", directiva="#8a5a1f", error="#b53a26",
                  aviso="#8f5f00", info="#1d62a0"),
}


def paleta_modo(modo):
    P = OSCURO if modo == "oscuro" else CLARO
    fondo, texto = P["vista"], P["texto"]
    S = {k: legible(v, fondo, texto) for k, v in SINTAXIS[modo].items()}
    return P, fondo, texto, S


def rgb(h):
    return "%d,%d,%d" % a_rgb(h)


# --- Konsole ------------------------------------------------------------------------------
def konsole(modo):
    P, fondo, texto, S = paleta_modo(modo)
    osc = modo == "oscuro"
    ansi = ([P["borde"], P["coral"], "#8cc093", P["neutro"], P["enlace"], P["visitado"], "#79b5ad", "#d9d2c0"] if osc
            else ["#3d3a3c", "#b53a26", "#2b7a4b", "#8f5f00", "#1d62a0", "#6a54b8", "#2f6f68", "#6b655d"])
    ansi = [a if i == 0 else legible(a, fondo, texto, 3.0) for i, a in enumerate(ansi)]
    fuerte = [mezclar(c, "#ffffff" if osc else "#000000", 0.18) for c in ansi]
    debil = [mezclar(c, fondo, 0.45) for c in ansi]
    nombres = {"oscuro": "OweeKoi Oscuro", "claro": "OweeKoi Claro"}
    out = [f"[Background]\nColor={rgb(fondo)}\n", f"[BackgroundFaint]\nColor={rgb(fondo)}\n",
           f"[BackgroundIntense]\nColor={rgb(fondo)}\n", f"[Foreground]\nColor={rgb(texto)}\n",
           f"[ForegroundFaint]\nColor={rgb(mezclar(texto, fondo, 0.4))}\n",
           f"[ForegroundIntense]\nColor={rgb(mezclar(texto, '#ffffff' if osc else '#000000', 0.15))}\n"]
    for i in range(8):
        out += [f"[Color{i}]\nColor={rgb(ansi[i])}\n", f"[Color{i}Faint]\nColor={rgb(debil[i])}\n",
                f"[Color{i}Intense]\nColor={rgb(fuerte[i])}\n"]
    out.append(f"[General]\nAnchor=0.5,0.5\nBlur=false\nColorRandomization=false\nDescription={nombres[modo]}\n"
               f"FillStyle=Tile\nOpacity=1\nWallpaper=\n")
    return "\n".join(out)


KONSOLE_PERFIL = """[Appearance]
ColorScheme={esquema}

[General]
Name=OweeKoi
Parent=FALLBACK/
"""


# --- Kate / KSyntaxHighlighting --------------------------------------------------------------
def kate(modo):
    P, fondo, texto, S = paleta_modo(modo)
    osc = modo == "oscuro"

    def e(color, **kw):
        d = {"text-color": color, "selected-text-color": color, "bold": False, "italic": False,
             "underline": False, "strike-through": False}
        d.update(kw)
        return d

    seleccion = mezclar(fondo, P["seleccion"], 0.30 if osc else 0.45)
    estilos = {
        "Normal": e(texto), "Keyword": e(S["palabra"], bold=True), "Function": e(S["funcion"]),
        "Variable": e(texto), "ControlFlow": e(S["palabra"], bold=True), "Operator": e(mezclar(texto, fondo, 0.2)),
        "BuiltIn": e(S["tipo"]), "Extension": e(S["funcion"]), "Preprocessor": e(S["directiva"]),
        "Attribute": e(S["funcion"]), "Char": e(S["cadena"]), "SpecialChar": e(S["cadena"], bold=True),
        "String": e(S["cadena"]), "VerbatimString": e(S["cadena"]), "SpecialString": e(S["cadena"], bold=True),
        "Import": e(S["palabra"]), "DataType": e(S["tipo"]), "DecVal": e(S["numero"]), "BaseN": e(S["numero"]),
        "Float": e(S["numero"]), "Constant": e(S["constante"]), "Comment": e(S["comentario"], italic=True),
        "Documentation": e(legible(mezclar(S["comentario"], S["funcion"], 0.35), fondo, texto), italic=True),
        "Annotation": e(S["directiva"], italic=True), "CommentVar": e(S["comentario"], italic=True, bold=True),
        "RegionMarker": e(S["info"], **{"background-color": mezclar(fondo, S["info"], 0.18)}),
        "Information": e(S["info"]), "Warning": e(S["aviso"]),
        "Alert": e(S["error"], bold=True, **{"background-color": mezclar(fondo, S["error"], 0.22)}),
        "Error": e(S["error"], underline=True), "Others": e(S["funcion"]),
    }
    colores = {
        "background-color": fondo, "code-folding": mezclar(fondo, texto, 0.55), "bracket-matching": mezclar(fondo, P["seleccion"], 0.55),
        "current-line": mezclar(fondo, texto, 0.06), "icon-border": mezclar(fondo, P["base"], 0.6),
        "indentation-line": mezclar(fondo, texto, 0.14), "line-numbers": legible(mezclar(fondo, texto, 0.5), fondo, texto, 4.5),
        "current-line-number": texto, "mark-bookmark": S["info"], "mark-breakpoint-active": S["error"],
        "mark-breakpoint-reached": S["aviso"], "mark-breakpoint-disabled": S["comentario"],
        "mark-execution": S["funcion"], "mark-warning": S["aviso"], "mark-error": S["error"],
        "modified-lines": S["aviso"], "replace-highlight": mezclar(fondo, S["aviso"], 0.4),
        "saved-lines": S["funcion"], "search-highlight": mezclar(fondo, S["cadena"], 0.4),
        "text-selection": seleccion, "separator": mezclar(fondo, texto, 0.2),
        "spell-checking": S["error"], "tab-marker": mezclar(fondo, texto, 0.2),
        "template-background": mezclar(fondo, P["base"], 0.5), "template-placeholder": mezclar(fondo, S["funcion"], 0.3),
        "template-focused-placeholder": mezclar(fondo, S["funcion"], 0.5),
        "template-read-only-placeholder": mezclar(fondo, S["error"], 0.3), "word-wrap-marker": mezclar(fondo, texto, 0.12),
    }
    nombre = "OweeKoi Oscuro" if osc else "OweeKoi Claro"
    return json.dumps({"metadata": {"name": nombre, "revision": 1}, "text-styles": estilos,
                       "editor-colors": colores}, indent=2, ensure_ascii=False) + "\n"


# --- Qt Creator ----------------------------------------------------------------------------------
def qtcreator(modo):
    P, fondo, texto, S = paleta_modo(modo)
    osc = modo == "oscuro"
    nombre = "OweeKoi Oscuro" if osc else "OweeKoi Claro"
    linea = mezclar(fondo, texto, 0.06)
    sel = mezclar(fondo, P["seleccion"], 0.30 if osc else 0.45)
    estilos = [
        ("Text", dict(foreground=texto, background=fondo)), ("Link", dict(foreground=S["tipo"])),
        ("Selection", dict(background=sel)),
        ("LineNumber", dict(foreground=legible(mezclar(fondo, texto, 0.5), fondo, texto), background=mezclar(fondo, P["base"], 0.5))),
        ("SearchResult", dict(background=mezclar(fondo, S["cadena"], 0.4))),
        ("SearchScope", dict(background=mezclar(fondo, S["tipo"], 0.2))),
        ("Parentheses", dict(foreground=texto, background=mezclar(fondo, P["seleccion"], 0.55))),
        ("ParenthesesMismatch", dict(background=mezclar(fondo, S["error"], 0.45))),
        ("AutoComplete", dict(foreground=texto, background=mezclar(fondo, P["seleccion"], 0.25))),
        ("CurrentLine", dict(background=linea)), ("CurrentLineNumber", dict(foreground=S["funcion"], bold="true")),
        ("Occurrences", dict(background=mezclar(fondo, S["tipo"], 0.18))),
        ("Number", dict(foreground=S["numero"])), ("String", dict(foreground=S["cadena"])),
        ("Type", dict(foreground=S["tipo"])), ("Local", dict(foreground=texto)), ("Parameter", dict(foreground=texto, italic="true")),
        ("Global", dict(foreground=S["constante"])), ("Field", dict(foreground=S["funcion"])),
        ("Static", dict(foreground=S["constante"], italic="true")), ("VirtualMethod", dict(foreground=S["funcion"], italic="true")),
        ("Function", dict(foreground=S["funcion"])), ("Macro", dict(foreground=S["directiva"])),
        ("Keyword", dict(foreground=S["palabra"], bold="true")), ("Attribute", dict(foreground=S["funcion"])),
        ("PrimitiveType", dict(foreground=S["tipo"])), ("Punctuation", dict(foreground=mezclar(texto, fondo, 0.25))),
        ("Operator", dict(foreground=mezclar(texto, fondo, 0.2))), ("Preprocessor", dict(foreground=S["directiva"])),
        ("Label", dict(foreground=S["constante"])), ("Comment", dict(foreground=S["comentario"], italic="true")),
        ("DisabledCode", dict(foreground=S["comentario"])), ("VisualWhitespace", dict(foreground=mezclar(fondo, texto, 0.25))),
        ("AddedLine", dict(foreground=S["funcion"])), ("RemovedLine", dict(foreground=S["error"])),
        ("DiffFile", dict(foreground=S["tipo"], bold="true")), ("DiffLocation", dict(foreground=S["numero"])),
        ("Warning", dict(underlinecolor=S["aviso"], underlinestyle="WaveUnderline")),
        ("Error", dict(underlinecolor=S["error"], underlinestyle="WaveUnderline")),
        ("Info", dict(underlinecolor=S["info"], underlinestyle="WaveUnderline")),
        ("TestPass", dict(foreground=S["funcion"])), ("TestFail", dict(foreground=S["error"])),
    ]
    filas = "\n".join("  <style name=\"%s\" %s/>" % (n, " ".join(f'{k}="{v}"' for k, v in a.items())) for n, a in estilos)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<style-scheme version="1.0" name="{nombre}">\n{filas}\n</style-scheme>\n'


def verificar():
    """Informe de contraste de lo que se acaba de generar."""
    malos = 0
    for modo in ("oscuro", "claro"):
        P, fondo, texto, S = paleta_modo(modo)
        for k, v in S.items():
            c = contraste(v, fondo)
            if c < 4.5:
                malos += 1
                print(f"  BAJO  {modo} {k}: {c:.2f}")
        print(f"  {modo}: texto {contraste(texto, fondo):.1f}:1 · sintaxis entre "
              f"{min(contraste(v, fondo) for v in S.values()):.1f} y {max(contraste(v, fondo) for v in S.values()):.1f}:1")
    return malos


if __name__ == "__main__":
    for carpeta in ("konsole", "kate", "qtcreator"):
        (SALIDA / carpeta).mkdir(parents=True, exist_ok=True)
    for modo, etiqueta in (("oscuro", "Oscuro"), ("claro", "Claro")):
        (SALIDA / "konsole" / f"OweeKoi-{etiqueta}.colorscheme").write_text(konsole(modo), encoding="utf-8")
        (SALIDA / "kate" / f"OweeKoi-{etiqueta}.theme").write_text(kate(modo), encoding="utf-8")
        (SALIDA / "qtcreator" / f"OweeKoi-{etiqueta}.xml").write_text(qtcreator(modo), encoding="utf-8")
    (SALIDA / "konsole" / "OweeKoi.profile").write_text(KONSOLE_PERFIL.format(esquema="OweeKoi-Oscuro"), encoding="utf-8")
    print("generados:", sorted(str(p.relative_to(SALIDA)) for p in SALIDA.rglob("*") if p.is_file()))
    sys.exit(1 if verificar() else 0)
