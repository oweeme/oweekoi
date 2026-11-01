#!/usr/bin/env bash
# OweeKoi - tema de KDE Plasma 6: estilo oscuro tipo macOS, kois, protector de pantalla
# animado y ajustes de energia/rendimiento para portatiles y PCs.
#
# Uso: ./install.sh [opciones]      (no hace falta ser root; ver --sistema)
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARE="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"

# Temas de terceros (se descargan de GitHub, fijados a una version concreta)
WS_KDE=(https://github.com/vinceliuice/WhiteSur-kde.git cf4df59ce91004f7ea39358b1b8ff917d5c329f7)
WS_ICONS=(https://github.com/vinceliuice/WhiteSur-icon-theme.git 73d8040da51a9ed74e47c7366e7e9ff437601a5c)
WS_CURSORS=(https://github.com/vinceliuice/WhiteSur-cursors.git e190baf618ed95ee217d2fd45589bd309b37672b)

PERFIL=auto
WHITESUR=1
DOCK=1
BARRA=1
ENERGIA=1
BALOO=1
APLICAR=1
SISTEMA=0

uso() {
  cat <<EOF
OweeKoi - tema para KDE Plasma 6

Uso: ./install.sh [opciones]

  --perfil laptop|pc|auto   Ajustes de energia y rendimiento (por defecto: auto,
                            detecta si hay bateria)
  --sin-whitesur            No descarga WhiteSur (queda Breeze oscuro + iconos propios)
  --sin-dock                No crea el dock flotante inferior
  --sin-barra               No cambia la barra superior (menu global y reloj centrado)
  --sin-energia             No toca la configuracion de energia
  --mantener-baloo          No desactiva el indexador de archivos (Baloo)
  --solo-archivos           Solo copia archivos; no cambia la configuracion de Plasma
  --sistema                 Ademas ejecuta los ajustes de sistema que piden sudo
                            (arranque directo, pantalla de arranque con tu logo...)
  -h, --help                Esta ayuda

Todo lo que se cambia en tu configuracion se respalda antes en
  $SHARE/oweekoi/respaldo-<fecha>
y ./uninstall.sh lo puede restaurar.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --perfil) PERFIL="${2:-}"; shift ;;
    --sin-whitesur) WHITESUR=0 ;;
    --sin-dock) DOCK=0 ;;
    --sin-barra) BARRA=0 ;;
    --sin-energia) ENERGIA=0 ;;
    --mantener-baloo) BALOO=0 ;;
    --solo-archivos) APLICAR=0 ;;
    --sistema) SISTEMA=1 ;;
    -h|--help) uso; exit 0 ;;
    *) echo "Opcion desconocida: $1" >&2; uso >&2; exit 1 ;;
  esac
  shift
done

msg() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
aviso() { printf '\033[1;33m!!\033[0m %s\n' "$*" >&2; }
falta() { printf '\033[1;31mxx\033[0m %s\n' "$*" >&2; exit 1; }

# --- comprobaciones ---------------------------------------------------------
if command -v plasmashell >/dev/null 2>&1; then
  ver="$(plasmashell --version 2>/dev/null | awk '{print $2}' || true)"
  if [ -z "$ver" ]; then
    aviso "No pude saber la version de Plasma; asumo que es la 6."
  elif [ "${ver%%.*}" -lt 6 ]; then
    falta "Hace falta KDE Plasma 6 (tienes $ver)."
  fi
else
  aviso "No encuentro plasmashell; copio los archivos pero no aplico nada."
  APLICAR=0
fi

if [ "$APLICAR" -eq 1 ]; then
  for c in kwriteconfig6 kreadconfig6 lookandfeeltool; do
    command -v "$c" >/dev/null 2>&1 || falta "Falta el comando $c (paquete de Plasma 6)."
  done
  [ -n "${WAYLAND_DISPLAY:-}${DISPLAY:-}" ] || {
    aviso "No hay sesion grafica activa; solo copio archivos."
    APLICAR=0
  }
fi

if [ "$PERFIL" = auto ]; then
  if ls /sys/class/power_supply/BAT* >/dev/null 2>&1; then PERFIL=laptop; else PERFIL=pc; fi
fi
case "$PERFIL" in laptop|pc) ;; *) falta "Perfil no valido: $PERFIL (usa laptop, pc o auto)";; esac
msg "Perfil: $PERFIL"

# --- respaldo ---------------------------------------------------------------
RESPALDO="$SHARE/oweekoi/respaldo-$(date +%Y%m%d-%H%M%S)"
if [ "$APLICAR" -eq 1 ]; then
  mkdir -p "$RESPALDO"
  for f in kdeglobals kcminputrc kscreenlockerrc ksplashrc powerdevilrc plasmarc kwinrc \
           plasma-org.kde.plasma.desktop-appletsrc plasmashellrc; do
    [ -f "$CONFIG/$f" ] && cp -a "$CONFIG/$f" "$RESPALDO/"
  done
  msg "Respaldo de tu configuracion en $RESPALDO"
fi

# --- 1. archivos del tema ---------------------------------------------------
msg "Instalando fondos, protector de pantalla y pantalla de inicio"
mkdir -p "$SHARE/wallpapers" "$SHARE/plasma/wallpapers" "$SHARE/plasma/look-and-feel"
for d in "$AQUI"/tema/wallpapers/*/; do
  rm -rf "$SHARE/wallpapers/$(basename "$d")"; cp -r "$d" "$SHARE/wallpapers/"
done
rm -rf "$SHARE/plasma/wallpapers/org.owee.koi"
cp -r "$AQUI/tema/plasma/wallpapers/org.owee.koi" "$SHARE/plasma/wallpapers/"
rm -rf "$SHARE/plasma/look-and-feel/org.owee.koi"
cp -r "$AQUI/tema/plasma/look-and-feel/org.owee.koi" "$SHARE/plasma/look-and-feel/"

msg "Creando el tema de iconos OweeLogo"
ICONOS="$SHARE/icons/OweeLogo"
rm -rf "$ICONOS"
dirs=""
for s in 16 22 24 32 48 64 128 256 512; do
  mkdir -p "$ICONOS/places/$s"
  for n in start-here-kde-neon start-here-kde start-here-kde-plasma start-here \
           distributor-logo-neon distributor-logo neon oweelogo; do
    cp "$AQUI/tema/iconos/$s/oweelogo.png" "$ICONOS/places/$s/$n.png"
  done
  dirs="$dirs${dirs:+,}places/$s"
done
{
  printf '[Icon Theme]\nName=OweeLogo\nComment=Logo de Owee sobre WhiteSur-dark\n'
  printf 'Inherits=WhiteSur-dark,breeze,hicolor\nDirectories=%s\n' "$dirs"
  for s in 16 22 24 32 48 64 128 256 512; do
    printf '\n[places/%s]\nSize=%s\nContext=Places\nType=Fixed\n' "$s" "$s"
  done
} > "$ICONOS/index.theme"
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$ICONOS" >/dev/null 2>&1 || true

# --- 2. WhiteSur ------------------------------------------------------------
descargar() { # url sha destino
  git init -q "$3"
  git -C "$3" remote add origin "$1"
  git -C "$3" fetch -q --depth 1 origin "$2"
  git -C "$3" checkout -q FETCH_HEAD
}
if [ "$WHITESUR" -eq 1 ] && [ "$APLICAR" -eq 1 ]; then
  command -v git >/dev/null 2>&1 || falta "Hace falta git para descargar WhiteSur (o usa --sin-whitesur)."
  msg "Descargando WhiteSur (vinceliuice) de GitHub, version fijada"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  descargar "${WS_KDE[0]}" "${WS_KDE[1]}" "$TMP/kde"
  descargar "${WS_ICONS[0]}" "${WS_ICONS[1]}" "$TMP/iconos"
  descargar "${WS_CURSORS[0]}" "${WS_CURSORS[1]}" "$TMP/cursores"
  (cd "$TMP/kde" && ./install.sh -c dark >/dev/null)
  (cd "$TMP/iconos" && ./install.sh -a -b >/dev/null)
  (cd "$TMP/cursores" && ./install.sh >/dev/null)
fi

[ "$APLICAR" -eq 1 ] || { msg "Archivos copiados. Nada mas se ha cambiado (--solo-archivos / sin sesion)."; exit 0; }

# --- 3. aplicar -------------------------------------------------------------
k() { kwriteconfig6 --file "$@"; }

if [ "$WHITESUR" -eq 1 ]; then
  msg "Aplicando WhiteSur oscuro"
  lookandfeeltool -a com.github.vinceliuice.WhiteSur-dark >/dev/null 2>&1 || aviso "No pude aplicar el tema global."
  command -v plasma-apply-colorscheme >/dev/null && plasma-apply-colorscheme WhiteSurDark >/dev/null 2>&1 || true
  command -v plasma-apply-cursortheme >/dev/null && plasma-apply-cursortheme WhiteSur-cursors >/dev/null 2>&1 || true
else
  lookandfeeltool -a org.kde.breezedark.desktop >/dev/null 2>&1 || true
fi

msg "Aplicando icono, fondo, bloqueo y pantalla de inicio de OweeKoi"
k kdeglobals --group Icons --key Theme OweeLogo
for p in /usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons /usr/libexec/plasma-changeicons; do
  [ -x "$p" ] && "$p" OweeLogo >/dev/null 2>&1 && break
done
k ksplashrc --group KSplash --key Theme org.owee.koi
k kscreenlockerrc --group Greeter --key WallpaperPlugin org.owee.koi
k kscreenlockerrc --group Daemon --key Autolock true
k kscreenlockerrc --group Daemon --key Timeout 5
k kscreenlockerrc --group Daemon --key LockOnResume true
k kscreenlockerrc --group Daemon --key LockGrace 5
command -v plasma-apply-wallpaperimage >/dev/null &&
  plasma-apply-wallpaperimage "$SHARE/wallpapers/OweeKoi-oscuro/contents/images/2560x1440.png" >/dev/null 2>&1 || true

if fc-list 2>/dev/null | grep -qi 'Inter:'; then
  msg "Aplicando la fuente Inter"
  f="Inter,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
  k kdeglobals --group General --key font "$f"
  k kdeglobals --group General --key menuFont "$f"
  k kdeglobals --group General --key toolBarFont "$f"
  k kdeglobals --group WM --key activeFont "Inter,10,-1,5,600,0,0,0,0,0,0,0,0,0,0,1"
fi

# --- 4. energia -------------------------------------------------------------
if [ "$ENERGIA" -eq 1 ]; then
  msg "Ajustes de energia (perfil $PERFIL)"
  # powerdevil reescribe su archivo al pararse: hay que escribir con el parado
  systemctl --user stop plasma-powerdevil.service 2>/dev/null || true
  e() { k powerdevilrc --group "$1" --group "$2" --key "$3" "$4"; }
  # Los kois salen al bloquear (min 5); la pantalla se apaga despues
  e AC Display DimDisplayIdleTimeoutSec 840
  e AC Display TurnOffDisplayIdleTimeoutSec 900
  e AC Display TurnOffDisplayIdleTimeoutWhenLockedSec 600
  e AC Performance PowerProfile balanced
  if [ "$PERFIL" = laptop ]; then
    e AC SuspendAndShutdown AutoSuspendIdleTimeoutSec 1800
    e Battery Display DimDisplayIdleTimeoutSec 540
    e Battery Display TurnOffDisplayIdleTimeoutSec 600
    e Battery Display TurnOffDisplayIdleTimeoutWhenLockedSec 300
    e Battery Performance PowerProfile power-saver
    e Battery SuspendAndShutdown AutoSuspendAction 1
    e Battery SuspendAndShutdown AutoSuspendIdleTimeoutSec 900
    e LowBattery Display DimDisplayIdleTimeoutSec 60
    e LowBattery Display TurnOffDisplayIdleTimeoutSec 120
    e LowBattery Performance PowerProfile power-saver
    e LowBattery SuspendAndShutdown AutoSuspendIdleTimeoutSec 300
  else
    e AC SuspendAndShutdown AutoSuspendIdleTimeoutSec 3600
  fi
  systemctl --user start plasma-powerdevil.service 2>/dev/null || true
fi

if [ "$BALOO" -eq 1 ] && command -v balooctl6 >/dev/null 2>&1; then
  msg "Desactivando el indexador de archivos Baloo (menos CPU y disco; usa --mantener-baloo para evitarlo)"
  balooctl6 disable >/dev/null 2>&1 || true
  balooctl6 purge >/dev/null 2>&1 || true
fi

# --- 5. dock ----------------------------------------------------------------
if [ "$DOCK" -eq 1 ] && command -v qdbus6 >/dev/null 2>&1; then
  msg "Dock flotante inferior"
  lanzadores=""
  for id in org.kde.dolphin org.kde.konsole org.kde.kate firefox google-chrome chromium \
            OweeCode oweestudent oweecapture org.kde.discover systemsettings; do
    for d in /usr/share/applications /var/lib/flatpak/exports/share/applications \
             "$SHARE/flatpak/exports/share/applications" /var/lib/snapd/desktop/applications \
             "$SHARE/applications"; do
      if [ -f "$d/$id.desktop" ]; then
        lanzadores="$lanzadores${lanzadores:+,}\"applications:$id.desktop\""
        break
      fi
    done
  done
  js="$(sed "s#__LANZADORES__#[$lanzadores]#" "$AQUI/lib/dock.js")"
  qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$js" >/dev/null 2>&1 ||
    aviso "No pude crear el dock (Plasma no responde)."
fi

# --- 5b. barra superior -----------------------------------------------------
if [ "$BARRA" -eq 1 ] && command -v qdbus6 >/dev/null 2>&1 && pgrep -x plasmashell >/dev/null; then
  msg "Barra superior: menu global y reloj centrado"
  res="$(qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \
        "$(cat "$AQUI/lib/barra.js")" 2>/dev/null || true)"
  panel="$(printf '%s' "$res" | sed -n 's/.*PANEL=\([0-9]*\) .*/\1/p')"
  orden="$(printf '%s' "$res" | sed -n 's/.*ORDER=\([0-9;]*\).*/\1/p')"
  if [ -n "$panel" ] && [ -n "$orden" ]; then
    actual="$(kreadconfig6 --file plasma-org.kde.plasma.desktop-appletsrc \
              --group Containments --group "$panel" --group General --key AppletOrder)"
    if [ "$actual" != "$orden" ]; then
      # El orden solo se puede fijar con Plasma parado; se reinicia unos segundos
      kquitapp6 plasmashell >/dev/null 2>&1 || true
      sleep 3
      kwriteconfig6 --file plasma-org.kde.plasma.desktop-appletsrc \
        --group Containments --group "$panel" --group General --key AppletOrder "$orden"
      (setsid kstart plasmashell >/dev/null 2>&1 &)
      sleep 5
    fi
  else
    aviso "No encontre la barra superior; la dejo como esta."
  fi
fi

# --- 6. sistema -------------------------------------------------------------
if [ "$SISTEMA" -eq 1 ]; then
  msg "Ajustes de sistema (piden sudo)"
  sudo bash "$AQUI/lib/sistema.sh" --perfil "$PERFIL"
fi

cat <<EOF

Listo. Cierra sesion y vuelve a entrar para ver el icono, la fuente y la pantalla de inicio.
  - El protector de pantalla (kois nadando) aparece al bloquear, a los 5 minutos sin actividad.
  - Para deshacer: ./uninstall.sh
EOF
[ "$SISTEMA" -eq 1 ] || echo "  - Arranque directo y logo en la pantalla de arranque: ./install.sh --sistema"
