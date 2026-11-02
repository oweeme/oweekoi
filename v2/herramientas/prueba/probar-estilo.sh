#!/usr/bin/env bash
# Dibuja los controles de Qt con el estilo OweeKoi (Union), en modo claro y oscuro, SIN tocar tu sesion:
# usa el estilo directamente desde el repositorio (v2/estilo/oweekoi) y una configuracion temporal.
#
# Uso: ./v2/herramientas/prueba/probar-estilo.sh [carpeta-de-salida]      (por defecto /tmp/oweekoi-prueba)
#   galeria-{oscuro,claro}.png   ventana con todos los controles
#   estados-{oscuro,claro}.png   cada control en reposo, raton encima, foco, pulsado, marcado y desactivado
#   paleta-{oscuro,claro}.txt    colores que KDE le da a Qt (incluye los de "desactivado")
# Necesita: g++, qt6-base-dev y Plasma 6.8 con Union. Edita v2/estilo/oweekoi/contents/css/*.css y repite.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V2="$(cd "$AQUI/../.." && pwd)"
OUT="${1:-/tmp/oweekoi-prueba}"
mkdir -p "$OUT/bin" "$OUT/datos/union/styles"
ln -sfn "$V2/estilo/oweekoi" "$OUT/datos/union/styles/oweekoi"

command -v g++ >/dev/null && pkg-config --exists Qt6Widgets || { echo "Falta g++ y qt6-base-dev" >&2; exit 1; }
for f in galeria estados paleta-qt; do
  [ "$OUT/bin/$f" -nt "$AQUI/$f.cpp" ] ||
    g++ -fPIC -std=c++17 -Wno-deprecated-declarations "$AQUI/$f.cpp" -o "$OUT/bin/$f" $(pkg-config --cflags --libs Qt6Widgets)
done

for modo in oscuro claro; do
  esquema="OweeKoi$([ "$modo" = oscuro ] && echo Dark || echo Light)"
  mkdir -p "$OUT/cfg-$modo"
  # kdeglobals temporal que solo contiene el esquema del repositorio
  python3 - "$V2/colores/$esquema.colors" "$OUT/cfg-$modo/kdeglobals" "$esquema" <<'PY'
import configparser, sys
src = configparser.RawConfigParser(); src.optionxform = str; src.read(sys.argv[1], encoding="utf-8")
dst = configparser.RawConfigParser(); dst.optionxform = str
for s in src.sections():
    dst.add_section(s)
    for k, v in src[s].items():
        dst[s][k] = v
dst["General"]["ColorScheme"] = sys.argv[3]
with open(sys.argv[2], "w", encoding="utf-8") as f:
    dst.write(f, space_around_delimiters=False)
PY
  export QT_QPA_PLATFORM=offscreen XDG_CURRENT_DESKTOP=KDE QT_FORCE_STDERR_LOGGING=1 QT_QPA_PLATFORMTHEME=kde \
         UNION_DISABLE_STYLE_CACHE=1 UNION_STYLE_NAME=oweekoi XDG_CONFIG_HOME="$OUT/cfg-$modo" XDG_DATA_HOME="$OUT/datos"
  timeout 40 "$OUT/bin/galeria" "$OUT/galeria-$modo.png" -style Union >/dev/null 2>&1
  timeout 40 "$OUT/bin/estados" "$OUT/estados-$modo.png" -style Union >/dev/null 2>&1
  timeout 40 "$OUT/bin/paleta-qt" -style Union > "$OUT/paleta-$modo.txt" 2>&1 || true
  echo "$modo: $OUT/galeria-$modo.png  $OUT/estados-$modo.png"
done
