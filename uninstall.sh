#!/usr/bin/env bash
# Quita OweeKoi y restaura la configuracion de Plasma que habia antes de instalar.
# No desinstala WhiteSur ni lo que haya instalado el modo --sistema.
set -euo pipefail

SHARE="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"

ULTIMO="$(ls -1d "$SHARE"/oweekoi/respaldo-* 2>/dev/null | sort | tail -1 || true)"

if [ -n "$ULTIMO" ]; then
  echo "==> Restaurando la configuracion desde $ULTIMO"
  systemctl --user stop plasma-powerdevil.service 2>/dev/null || true
  for f in "$ULTIMO"/*; do
    cp -a "$f" "$CONFIG/$(basename "$f")"
  done
  systemctl --user start plasma-powerdevil.service 2>/dev/null || true
else
  echo "No hay respaldo de configuracion; solo se quitan los archivos del tema."
fi

echo "==> Quitando archivos de OweeKoi"
rm -rf "$SHARE"/wallpapers/OweeKoi-* \
       "$SHARE/plasma/wallpapers/org.owee.koi" \
       "$SHARE/plasma/look-and-feel/org.owee.koi" \
       "$SHARE/icons/OweeLogo"

cat <<EOF

Hecho. Cierra sesion y vuelve a entrar.
Si quieres borrar tambien los respaldos: rm -rf "$SHARE/oweekoi"
El dock inferior no se quita solo: clic derecho sobre el dock > Editar panel > Eliminar panel.
EOF
