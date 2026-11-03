#!/usr/bin/env bash
# Quita OweeKoi 2 y restaura la configuracion de Plasma que habia antes de instalar.
set -euo pipefail

SHARE="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
BIN="${OWEE_BIN:-$HOME/.local/bin}"

ULTIMO="$(ls -1d "$SHARE"/oweekoi/respaldo-v2-* 2>/dev/null | sort | tail -1 || true)"

"$BIN/owee-estilo" desactivar >/dev/null 2>&1 || true
"$BIN/owee-animaciones" restaurar >/dev/null 2>&1 || true
systemctl --user disable --now oweekoi-tema.timer >/dev/null 2>&1 || true
rm -f "$CONFIG/systemd/user/oweekoi-tema.service" "$CONFIG/systemd/user/oweekoi-tema.timer"

if [ -n "$ULTIMO" ]; then
  echo "==> Restaurando la configuracion desde $ULTIMO"
  for f in "$ULTIMO"/*; do
    cp -a "$f" "$CONFIG/$(basename "$f")"
  done
else
  echo "No hay respaldo de la v2; solo se quitan los archivos del tema."
fi

echo "==> Quitando archivos de OweeKoi 2"
rm -rf "$SHARE"/color-schemes/OweeKoiDark.colors "$SHARE"/color-schemes/OweeKoiLight.colors \
       "$SHARE/icons/OweeKoi" "$SHARE/icons/OweeKoi-Punteros" "$HOME/.icons/OweeKoi-Punteros" "$SHARE/union/styles/oweekoi" "$SHARE/wallpapers/OweeKoi-Estanque" \
       "$SHARE/plasma/wallpapers/org.owee.koi" "$SHARE/plasma/desktoptheme/OweeKoi-Onda" \
       "$SHARE"/plasma/look-and-feel/org.owee.koi "$SHARE"/plasma/look-and-feel/org.owee.koi.oscuro \
       "$SHARE"/plasma/look-and-feel/org.owee.koi.claro \
       "$SHARE/aurorae/themes/OweeKoi-Onda-Dark" "$SHARE/aurorae/themes/OweeKoi-Onda-Light" \
       "$SHARE/kio/servicemenus/oweekoi-color-carpeta.desktop" \
       "$SHARE"/konsole/OweeKoi-Oscuro.colorscheme "$SHARE"/konsole/OweeKoi-Claro.colorscheme "$SHARE/konsole/OweeKoi.profile" \
       "$SHARE"/org.kde.syntax-highlighting/themes/OweeKoi-Oscuro.theme "$SHARE"/org.kde.syntax-highlighting/themes/OweeKoi-Claro.theme \
       "$CONFIG"/QtProject/qtcreator/styles/OweeKoi-Oscuro.xml "$CONFIG"/QtProject/qtcreator/styles/OweeKoi-Claro.xml \
       "$BIN/owee-tema" "$BIN/owee-carpeta" "$BIN/owee-animaciones" "$BIN/owee-estilo"

cat <<EOF

Hecho. Cierra sesion y vuelve a entrar.
Las carpetas a las que les pusiste color conservan un archivo oculto ".directory"; puedes
borrarlo desde Dolphin (mostrar archivos ocultos) o dejarlo: no hace dano.
Si instalaste el login:  sudo ./v2/login/instalar-login.sh --quitar
Para borrar tambien los respaldos: rm -rf "$SHARE/oweekoi"
EOF
