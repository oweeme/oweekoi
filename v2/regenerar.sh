#!/usr/bin/env bash
# Regenera TODO lo generado de OweeKoi 2 a partir de v2/herramientas/paleta.py y de los generadores.
#
# Uso: ./v2/regenerar.sh              regenera todo, en orden
#      ./v2/regenerar.sh colores      regenera solo una pieza (ver la lista con --lista)
#      ./v2/regenerar.sh --lista
#
# Despues de regenerar, instala con:  ./v2/instalar.sh
# Lo que NO se genera y se edita a mano: v2/estilo/oweekoi (CSS), v2/herramientas/owee-* (scripts),
# v2/integracion/, v2/instalar.sh y v2/login/. Mira docs/MANUAL.md.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
H="$AQUI/herramientas"

# nombre : script : que genera : depende de
PIEZAS=(
  "colores|generar_colores.py|Esquemas de color claro y oscuro de KDE (v2/colores)"
  "carpetas|generar_carpetas.py|Tema de iconos: carpetas de colores y logo (v2/iconos)"
  "punteros|generar_punteros.py|Cursores: flecha, puntero con onda y logo al cargar (v2/punteros; necesita xcursorgen)"
  "fondos|generar_fondos.py|Fondos del estanque, claro y oscuro, y agua del protector (v2/fondos, v2/plasma/wallpapers)"
  "ventanas|generar_onda.py|Decorado de ventanas Onda, claro y oscuro (v2/ventanas)"
  "plasma|generar_plasma.py|Estilo de Plasma: paneles, menus y dialogos (v2/plasma/desktoptheme)"
  "globales|generar_temas_globales.py|Temas globales Oscuro y Claro, con su disposicion (v2/plasma/look-and-feel; usa los fondos)"
  "editores|generar_editores.py|Temas de Konsole, Kate y Qt Creator (v2/editores)"
)

if [ "${1:-}" = "--lista" ] || [ "${1:-}" = "-h" ]; then
  printf '%-10s %s\n' "PIEZA" "QUE GENERA"
  for p in "${PIEZAS[@]}"; do IFS='|' read -r n s d <<< "$p"; printf '%-10s %s\n' "$n" "$d"; done
  exit 0
fi

command -v python3 >/dev/null || { echo "Falta python3" >&2; exit 1; }
python3 -c "import PIL, numpy" 2>/dev/null || { echo "Faltan Pillow y numpy (sudo apt install python3-pil python3-numpy)" >&2; exit 1; }

ok=0
for p in "${PIEZAS[@]}"; do
  IFS='|' read -r nombre script desc <<< "$p"
  if [ -n "${1:-}" ] && [ "$1" != "$nombre" ]; then continue; fi
  printf '\033[1;32m==>\033[0m %-9s %s\n' "$nombre" "$desc"
  # -I: aislado, no carga nada del directorio actual
  python3 -I "$H/$script" | sed 's/^/      /' | tail -4
  ok=$((ok + 1))
done
[ "$ok" -gt 0 ] || { echo "No existe la pieza '$1'. Mira: $0 --lista" >&2; exit 1; }
echo "Listo ($ok pieza(s)). Para instalar:  ./v2/instalar.sh"
