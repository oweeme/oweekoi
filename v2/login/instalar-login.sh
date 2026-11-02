#!/usr/bin/env bash
# OweeKoi 2 - login. Copia el tema a /usr/share para que el Plasma Login Manager pueda usarlo.
#
# Por que hace falta: la pantalla de login corre como el usuario "plasmalogin", que no puede
# leer tu carpeta personal. Este script solo copia archivos; NO edita la configuracion del login:
# eso lo haces tu desde Configuracion del sistema (ver los pasos al final).
#
# Uso:  sudo ./v2/login/instalar-login.sh          copia el tema a /usr/share
#       sudo ./v2/login/instalar-login.sh --quitar  quita lo que copio
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"     # carpeta v2/
PREFIJO="${PREFIJO:-/usr}"                                   # solo cambia en las pruebas
MODO=instalar
[ "${1:-}" = "--quitar" ] && MODO=quitar

if [ "$PREFIJO" = /usr ] && [ "$(id -u)" -ne 0 ]; then
  echo "Hace falta sudo:  sudo $0 $*" >&2
  exit 1
fi

S="$PREFIJO/share"
DESTINOS=(
  "$S/plasma/wallpapers/org.owee.koi"
  "$S/wallpapers/OweeKoi-Estanque"
  "$S/icons/OweeKoi"
  "$S/plasma/desktoptheme/OweeKoi-Onda"
  "$S/color-schemes/OweeKoiDark.colors"
  "$S/color-schemes/OweeKoiLight.colors"
)

if [ "$MODO" = quitar ]; then
  rm -rf "${DESTINOS[@]}"
  echo "Quitado. En Configuracion del sistema > Pantalla de inicio de sesion elige otro fondo."
  exit 0
fi

echo "==> Copiando el tema a $S"
install -d "$S/plasma/wallpapers" "$S/wallpapers" "$S/icons" "$S/plasma/desktoptheme" "$S/color-schemes"
rm -rf "${DESTINOS[@]}"
cp -r "$AQUI/plasma/wallpapers/org.owee.koi"      "$S/plasma/wallpapers/"
cp -r "$AQUI/fondos/OweeKoi-Estanque"             "$S/wallpapers/"
cp -r "$AQUI/iconos/OweeKoi"                      "$S/icons/"
cp -r "$AQUI/plasma/desktoptheme/OweeKoi-Onda"    "$S/plasma/desktoptheme/"
cp "$AQUI"/colores/OweeKoiDark.colors "$AQUI"/colores/OweeKoiLight.colors "$S/color-schemes/"
# permisos de lectura para todos (el usuario "plasmalogin" tiene que poder leerlos)
chmod -R a+rX "${DESTINOS[@]}"
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$S/icons/OweeKoi" >/dev/null 2>&1 || true

cat <<'EOF'

Listo. Ahora, sin sudo y en tu sesion:
  1. Abre  Configuracion del sistema > Pantalla de inicio de sesion  (Login Screen).
  2. En Apariencia, en el tipo de fondo elige  "Owee Koi (animado)".
  3. Usa el boton para sincronizar tus ajustes de Plasma con la pantalla de inicio de sesion
     (colores, estilo, iconos y cursor). Te pedira tu contrasena.
  4. Para verlo: cierra sesion (o reinicia). Para deshacerlo: el mismo modulo, restablecer.
Para quitar lo copiado:  sudo ./v2/login/instalar-login.sh --quitar
EOF
