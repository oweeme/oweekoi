#!/usr/bin/env bash
# Ajustes de sistema de OweeKoi (necesitan root). Lo lanza ./install.sh --sistema
# o a mano: sudo bash lib/sistema.sh --perfil laptop|pc
#
# Cada paso se salta solo si tu sistema no lo admite. No borra paquetes.
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PERFIL=pc
[ "${1:-}" = "--perfil" ] && PERFIL="${2:-pc}"

[ "$(id -u)" -eq 0 ] || { echo "Ejecuta con sudo." >&2; exit 1; }

paso() { printf '\n\033[1;32m==>\033[0m %s\n' "$*"; }
salto() { printf '    (omitido: %s)\n' "$*"; }

# 1. GRUB sin menu tras un apagado forzado. GRUB muestra su menu 30 s cuando el
#    arranque anterior no termino bien ("recordfail"); aqui se desactiva.
paso "Arranque directo (sin esperar el menu de GRUB tras un apagado forzado)"
if [ -f /etc/default/grub ] && command -v update-grub >/dev/null 2>&1; then
  if grep -q '^GRUB_RECORDFAIL_TIMEOUT=' /etc/default/grub; then
    sed -i 's/^GRUB_RECORDFAIL_TIMEOUT=.*/GRUB_RECORDFAIL_TIMEOUT=0/' /etc/default/grub
  else
    echo 'GRUB_RECORDFAIL_TIMEOUT=0' >> /etc/default/grub
  fi
  update-grub
else
  salto "no hay GRUB con update-grub"
fi

# 2. TRIM del SSD
paso "TRIM semanal del SSD"
if systemctl list-unit-files fstrim.timer >/dev/null 2>&1; then
  systemctl enable --now fstrim.timer
else
  salto "no existe fstrim.timer"
fi

# 3. No esperar la red al arrancar
paso "No esperar a la red para llegar al escritorio"
if systemctl is-enabled NetworkManager-wait-online.service >/dev/null 2>&1; then
  systemctl disable NetworkManager-wait-online.service
else
  salto "NetworkManager-wait-online no esta activo"
fi

# 4. Fuente Inter
paso "Fuente Inter"
if command -v apt-get >/dev/null 2>&1; then
  apt-get install -y fonts-inter
else
  salto "instala la fuente Inter con tu gestor de paquetes"
fi

# 5. Portatil Intel: control termico
if [ "$PERFIL" = laptop ] && grep -q GenuineIntel /proc/cpuinfo && command -v apt-get >/dev/null 2>&1; then
  paso "thermald (control termico del procesador Intel)"
  apt-get install -y thermald
  systemctl enable --now thermald
fi

# 6. Pantalla de arranque (Plymouth) con el logo de Owee
paso "Pantalla de arranque con el logo de Owee"
BASE=/usr/share/plymouth/themes/breeze
DST=/usr/share/plymouth/themes/oweekoi
if [ -d "$BASE" ] && command -v update-alternatives >/dev/null 2>&1 \
   && command -v update-initramfs >/dev/null 2>&1 \
   && python3 -c 'import PIL' >/dev/null 2>&1; then
  rm -rf "$DST"
  cp -r "$BASE" "$DST"
  mv "$DST/breeze.plymouth" "$DST/oweekoi.plymouth"
  mv "$DST/breeze.script" "$DST/oweekoi.script"
  rm -f "$DST/breeze.grub"
  # sustituir cada logo del tema por el de Owee, con el mismo tamano
  python3 -I - "$AQUI/assets/owee-logo-512.png" "$DST/images" <<'PY'
import glob, os, sys
from PIL import Image
logo = Image.open(sys.argv[1]).convert("RGBA")
for f in glob.glob(os.path.join(sys.argv[2], "**", "*logo*.png"), recursive=True):
    ancho, alto = Image.open(f).size
    lado = min(ancho, alto)
    logo.resize((lado, lado), Image.LANCZOS).save(f)
PY
  sed -i 's#themes//breeze#themes/oweekoi#g; s#^Name=.*#Name=OweeKoi#; s#breeze.script#oweekoi.script#' \
    "$DST/oweekoi.plymouth"
  sed -i 's#^\(global.title.text *= *\)".*";#\1"Owee";#' "$DST/oweekoi.script"
  update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth \
    "$DST/oweekoi.plymouth" 200
  update-alternatives --set default.plymouth "$DST/oweekoi.plymouth"
  update-initramfs -u
  echo "    Para volver al tema anterior:"
  echo "    sudo update-alternatives --set default.plymouth $BASE/breeze.plymouth && sudo update-initramfs -u"
else
  salto "necesita Plymouth con tema breeze, update-initramfs y python3-pil"
fi

echo
echo "Listo. Reinicia para ver el arranque."
