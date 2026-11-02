#!/usr/bin/env bash
# Muestra el tamano que Qt (el mismo codigo que usa Plasma) ve para cada pieza de un marco SVG.
# Si una pieza mide 1 px de mas, el marco entero se descuadra: casi siempre es un trazo en su borde.
#
# Uso: ./v2/herramientas/prueba/medir-marco.sh <archivo.svg> [pieza ...]
#   ./v2/herramientas/prueba/medir-marco.sh v2/plasma/desktoptheme/OweeKoi-Onda/widgets/background.svg
# Esperado en los menus: topleft 24x24, top 20x24, left 24x20, center 20x20 (en el panel, todo 8x8).
set -euo pipefail
SVG="$(realpath "${1:?Falta el archivo .svg}")"; shift || true
PIEZAS=("${@:-topleft}"); [ $# -gt 0 ] || PIEZAS=(topleft top topright left center right bottomleft bottom bottomright shadow-topleft)
lista=$(printf '"%s",' "${PIEZAS[@]}"); lista="[${lista%,}]"
QML="$(mktemp --suffix=.qml)"; trap 'rm -f "$QML"' EXIT
cat > "$QML" <<QMLEOF
import QtQuick
import org.kde.ksvg as KSvg
Item {
    KSvg.Svg { id: s; imagePath: "$SVG" }
    Component.onCompleted: {
        var n = $lista;
        for (var i = 0; i < n.length; i++) { var t = s.elementSize(n[i]); console.log(n[i] + "  " + t.width + "x" + t.height); }
        Qt.quit()
    }
}
QMLEOF
QT_QPA_PLATFORM=offscreen QT_FORCE_STDERR_LOGGING=1 qml6 "$QML" 2>&1 | grep '^qml: ' | sed 's/^qml: //'
