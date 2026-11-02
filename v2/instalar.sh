#!/usr/bin/env bash
# OweeKoi 2 - tema propio para KDE Plasma 6: tinta y papel, ondas del estanque, carpetas de
# colores, fondos y protector de kois. No descarga nada de terceros (no usa WhiteSur).
#
# Uso: ./v2/instalar.sh [opciones]      (no hace falta ser root)
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
SHARE="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
BIN="${OWEE_BIN:-$HOME/.local/bin}"

MODO=auto
APLICAR=1
BARRA=1
ANIMACIONES=1
HORARIO=0
SIMULAR=0

uso() {
  cat <<EOF
OweeKoi 2 - tema para KDE Plasma 6

Uso: ./v2/instalar.sh [opciones]

  --modo claro|oscuro|auto  Modo con el que arranca (por defecto auto: claro de 07:00 a 19:00)
  --solo-archivos           Solo copia archivos; no cambia la configuracion de Plasma
  --sin-barra               No cambia la barra superior (menu global y reloj centrado)
  --sin-animaciones         No cambia las animaciones de KWin (Magic Lamp al minimizar, mas suaves)
  --horario                 Ademas activa un temporizador que cambia claro/oscuro segun la hora
  --simular                 Muestra lo que haria, sin tocar nada
  -h, --help                Esta ayuda

Antes de cambiar nada respalda tu configuracion en
  $SHARE/oweekoi/respaldo-v2-<fecha>
y ./v2/desinstalar.sh la restaura.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --modo) MODO="${2:-}"; shift ;;
    --solo-archivos) APLICAR=0 ;;
    --sin-barra) BARRA=0 ;;
    --sin-animaciones) ANIMACIONES=0 ;;
    --horario) HORARIO=1 ;;
    --simular) SIMULAR=1 ;;
    -h|--help) uso; exit 0 ;;
    *) echo "Opcion desconocida: $1" >&2; uso >&2; exit 1 ;;
  esac
  shift
done

msg() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
aviso() { printf '\033[1;33m!!\033[0m %s\n' "$*" >&2; }
falta() { printf '\033[1;31mxx\033[0m %s\n' "$*" >&2; exit 1; }

case "$MODO" in claro|oscuro|auto) ;; *) falta "Modo no valido: $MODO (usa claro, oscuro o auto)" ;; esac
if [ "$MODO" = auto ]; then
  h=$((10#$(date +%H)))
  if [ "$h" -ge 7 ] && [ "$h" -lt 19 ]; then MODO=claro; else MODO=oscuro; fi
fi

# --- comprobaciones ---------------------------------------------------------
if command -v plasmashell >/dev/null 2>&1; then
  ver="$(plasmashell --version 2>/dev/null | awk '{print $2}' || true)"
  [ -n "$ver" ] && [ "${ver%%.*}" -lt 6 ] && falta "Hace falta KDE Plasma 6 (tienes $ver)."
else
  aviso "No encuentro plasmashell; copio los archivos pero no aplico nada."
  APLICAR=0
fi
if [ "$APLICAR" -eq 1 ]; then
  for c in kwriteconfig6 kreadconfig6 plasma-apply-colorscheme plasma-apply-desktoptheme; do
    command -v "$c" >/dev/null 2>&1 || falta "Falta el comando $c (paquete de Plasma 6)."
  done
  [ -n "${WAYLAND_DISPLAY:-}${DISPLAY:-}" ] || { aviso "No hay sesion grafica activa; solo copio archivos."; APLICAR=0; }
fi

if [ "$SIMULAR" -eq 1 ]; then
  msg "Simulacion. Modo: $MODO · aplicar configuracion: $APLICAR · barra superior: $BARRA · horario: $HORARIO"
  echo "  Copiaria a $SHARE: color-schemes, icons/OweeKoi, wallpapers/OweeKoi-Estanque, plasma/{wallpapers,desktoptheme,look-and-feel}, aurorae/themes"
  echo "  Copiaria a $BIN: owee-tema, owee-carpeta; menu de Dolphin en $SHARE/kio/servicemenus"
  exit 0
fi

# --- respaldo ---------------------------------------------------------------
RESPALDO="$SHARE/oweekoi/respaldo-v2-$(date +%Y%m%d-%H%M%S)"
if [ "$APLICAR" -eq 1 ]; then
  mkdir -p "$RESPALDO"
  for f in kdeglobals kcminputrc kscreenlockerrc ksplashrc plasmarc kwinrc \
           plasma-org.kde.plasma.desktop-appletsrc plasmashellrc; do
    [ -f "$CONFIG/$f" ] && cp -a "$CONFIG/$f" "$RESPALDO/"
  done
  msg "Respaldo de tu configuracion en $RESPALDO"
fi

# --- 1. archivos ------------------------------------------------------------
msg "Instalando colores, iconos, fondos, estilo de Plasma y ventanas"
mkdir -p "$SHARE/color-schemes" "$SHARE/icons" "$SHARE/wallpapers" "$SHARE/plasma/wallpapers" \
         "$SHARE/plasma/desktoptheme" "$SHARE/plasma/look-and-feel" "$SHARE/aurorae/themes" \
         "$SHARE/kio/servicemenus" "$BIN"
cp "$AQUI"/colores/OweeKoi*.colors "$SHARE/color-schemes/"
rm -rf "$SHARE/icons/OweeKoi";                  cp -r "$AQUI/iconos/OweeKoi" "$SHARE/icons/"
command -v gtk-update-icon-cache >/dev/null 2>&1 &&
  gtk-update-icon-cache -f -t "$SHARE/icons/OweeKoi" >/dev/null 2>&1 || true
rm -rf "$SHARE/wallpapers/OweeKoi-Estanque";    cp -r "$AQUI/fondos/OweeKoi-Estanque" "$SHARE/wallpapers/"
rm -rf "$SHARE/plasma/wallpapers/org.owee.koi"; cp -r "$AQUI/plasma/wallpapers/org.owee.koi" "$SHARE/plasma/wallpapers/"
rm -rf "$SHARE/plasma/desktoptheme/OweeKoi-Onda"; cp -r "$AQUI/plasma/desktoptheme/OweeKoi-Onda" "$SHARE/plasma/desktoptheme/"
for d in "$AQUI"/plasma/look-and-feel/*/; do
  n="$(basename "$d")"; rm -rf "$SHARE/plasma/look-and-feel/$n"; cp -r "$d" "$SHARE/plasma/look-and-feel/"
done
for m in Dark Light; do
  rm -rf "$SHARE/aurorae/themes/OweeKoi-Onda-$m"; cp -r "$AQUI/ventanas/OweeKoi-Onda-$m" "$SHARE/aurorae/themes/"
done
msg "Instalando tus herramientas (owee-tema, owee-carpeta) y el menu Color de carpeta"
install -m 755 "$AQUI/herramientas/owee-tema" "$AQUI/herramientas/owee-carpeta" "$AQUI/herramientas/owee-animaciones" "$BIN/"
install -m 755 "$AQUI/integracion/dolphin/oweekoi-color-carpeta.desktop" "$SHARE/kio/servicemenus/"
case ":$PATH:" in *":$BIN:"*) ;; *) aviso "$BIN no esta en tu PATH; añadelo para usar owee-tema." ;; esac

[ "$APLICAR" -eq 1 ] || { msg "Archivos copiados. Nada mas se ha cambiado (--solo-archivos / sin sesion)."; exit 0; }

# --- 2. aplicar -------------------------------------------------------------
k() { kwriteconfig6 --file "$@"; }
msg "Aplicando OweeKoi ($MODO)"
plasma-apply-colorscheme "$([ "$MODO" = claro ] && echo OweeKoiLight || echo OweeKoiDark)" >/dev/null 2>&1 ||
  aviso "No pude aplicar el esquema de color."
k kdeglobals --group Icons --key Theme OweeKoi
for p in /usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons /usr/libexec/plasma-changeicons; do
  [ -x "$p" ] && "$p" OweeKoi >/dev/null 2>&1 && break
done
plasma-apply-desktoptheme OweeKoi-Onda >/dev/null 2>&1 || aviso "No pude aplicar el estilo de Plasma."
k kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
k kwinrc --group org.kde.kdecoration2 --key theme "__aurorae__svg__OweeKoi-Onda-$([ "$MODO" = claro ] && echo Light || echo Dark)"
command -v qdbus6 >/dev/null 2>&1 && qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
k ksplashrc --group KSplash --key Theme org.owee.koi
k kscreenlockerrc --group Greeter --key WallpaperPlugin org.owee.koi
k kscreenlockerrc --group Daemon --key Autolock true
k kscreenlockerrc --group Daemon --key Timeout 5
k kscreenlockerrc --group Daemon --key LockOnResume true
command -v plasma-apply-wallpaperimage >/dev/null 2>&1 &&
  plasma-apply-wallpaperimage "$SHARE/wallpapers/OweeKoi-Estanque" >/dev/null 2>&1 || true

# --- 3. barra superior ------------------------------------------------------
if [ "$BARRA" -eq 1 ] && command -v qdbus6 >/dev/null 2>&1 && pgrep -x plasmashell >/dev/null; then
  msg "Barra superior: menu global y reloj centrado"
  res="$(qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \
        "$(cat "$RAIZ/lib/barra.js")" 2>/dev/null || true)"
  panel="$(printf '%s' "$res" | sed -n 's/.*PANEL=\([0-9]*\) .*/\1/p')"
  orden="$(printf '%s' "$res" | sed -n 's/.*ORDER=\([0-9;]*\).*/\1/p')"
  if [ -n "$panel" ] && [ -n "$orden" ]; then
    actual="$(kreadconfig6 --file plasma-org.kde.plasma.desktop-appletsrc \
              --group Containments --group "$panel" --group General --key AppletOrder)"
    if [ "$actual" != "$orden" ]; then
      # El orden solo se puede fijar con Plasma parado; se reinicia unos segundos
      kquitapp6 plasmashell >/dev/null 2>&1 || true
      sleep 3
      k plasma-org.kde.plasma.desktop-appletsrc --group Containments --group "$panel" --group General \
        --key AppletOrder "$orden"
      (setsid kstart plasmashell >/dev/null 2>&1 &)
      sleep 5
    fi
  else
    aviso "No encontre la barra superior; la dejo como esta."
  fi
fi

# --- 3b. animaciones --------------------------------------------------------
if [ "$ANIMACIONES" -eq 1 ] && command -v qdbus6 >/dev/null 2>&1; then
  msg "Animaciones suaves (Magic Lamp al minimizar)"
  "$BIN/owee-animaciones" activar || aviso "No pude cambiar las animaciones."
fi

# --- 4. cambio automatico por hora (opcional) -------------------------------
if [ "$HORARIO" -eq 1 ]; then
  msg "Activando el cambio claro/oscuro por hora (temporizador de usuario)"
  mkdir -p "$CONFIG/systemd/user"
  cp "$AQUI"/integracion/systemd/oweekoi-tema.* "$CONFIG/systemd/user/"
  systemctl --user daemon-reload
  systemctl --user enable --now oweekoi-tema.timer
fi

cat <<EOF

Listo. Cierra sesion y vuelve a entrar para ver la pantalla de inicio y el protector.
  - Cambiar de modo:   owee-tema claro | oscuro | alternar | auto
  - Color de carpeta:  clic derecho en una carpeta de Dolphin > Actions > Color de carpeta
  - Animaciones:       owee-animaciones activar | restaurar
  - Login:             sudo ./v2/login/instalar-login.sh  (y luego Configuracion > Pantalla de inicio de sesion)
  - Para deshacer:     ./v2/desinstalar.sh
EOF
[ "$HORARIO" -eq 1 ] || echo "  - Cambio automatico por hora (opcional):  ./v2/instalar.sh --horario"
