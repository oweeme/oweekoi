"""Paleta de OweeKoi 2: una sola fuente de verdad para esquemas de color e iconos.

Sale del logo (verde #207860, crema #FDEBAB, coral #f85848, marron #483830) y del sitio de
Owee (oscuro con tono pizarra). Fondos nunca negro ni blanco puro: textos a ~12:1 de contraste,
no a 21:1, que cansa menos la vista. Todo el texto normal cumple WCAG AA (>= 4.5:1).
"""
import math

# Estilo "tinta y papel": oscuro = tinta sumi (negro pastel calido, sin tinte azul ni verde)
# con texto crema del logo; claro = papel crema con texto de tinta. Los dos se leen como
# inversion uno del otro. El verde lima y el coral del koi son los unicos acentos.
# acento_kde es el AccentColor de Plasma (el que eligio el autor): se escribe en el esquema.
OSCURO = dict(
    base="#232122", vista="#1b1a1b", superficie="#2a2829", elevado="#323031", borde="#4a4647",
    texto="#ece6d6", suave="#b0a99a", acento="#6fd45c", acento_kde="#3dd425",
    seleccion="#75de61", sobre_seleccion="#0f1d0b",
    coral="#f58a76", positivo="#7bd88f", neutro="#e8b65c", enlace="#7cb9f0", visitado="#b5a8f0",
)
CLARO = dict(
    base="#f2eee2", vista="#faf7ee", superficie="#ebe6d6", elevado="#fffdf7", borde="#d6cfbb",
    texto="#252223", suave="#5f5a55", acento="#2c991a", acento_kde="#3dd425",
    seleccion="#75de61", sobre_seleccion="#0f1d0b",
    coral="#c9412c", positivo="#2b7a4b", neutro="#8f5f00", enlace="#1d62a0", visitado="#6a54b8",
)

# Tonos (grados OKLCH) de las carpetas de colores; mismo brillo percibido para todos
CARPETAS = {
    "rojo": 25, "naranja": 55, "amarillo": 95, "verde": 150,
    "turquesa": 185, "azul": 240, "violeta": 290, "rosa": 350,
}
L_CARPETA, C_CARPETA = 0.72, 0.115


def a_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(h):
    r, g, b = map(_lin, a_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def oklch(L, C, grados):
    h = math.radians(grados)
    a, b = C * math.cos(h), C * math.sin(h)
    l_, m_, s_ = L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lineal = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
              -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
              -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    f = lambda x: 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(f(max(0, min(1, v))) * 255))) for v in lineal)


def color_carpeta(nombre, dL=0.0, dC=0.0):
    if nombre == "gris":
        return oklch(L_CARPETA + dL, 0.02 + dC, 170)
    return oklch(L_CARPETA + dL, C_CARPETA + dC, CARPETAS[nombre])
