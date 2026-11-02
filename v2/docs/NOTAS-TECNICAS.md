# OweeKoi 2 — Notas técnicas: lo que falló y por qué

Estas notas recogen los límites reales de KDE/Qt que encontramos construyendo el tema. Léelas antes de
cambiar las piezas gráficas: cada punto costó tiempo descubrirlo y evita volver a caer en lo mismo.

## 1. Dibujo SVG en Plasma, Aurorae y Union

**QtSvg ignora `clipPath`.** Recortar un dibujo grande para sacar las 9 piezas de un marco parece lógico,
pero Qt dibuja cada pieza con el marco entero apretado en su hueco: salen "pestañas" y bloques negros.
→ En las **ventanas** cada pieza es un PNG del tamaño exacto (a doble resolución). En **Plasma** cada pieza se
calcula como forma propia (arcos y rectángulos), sin recortar nada.

**Qt mide una pieza contando el grosor de los trazos.** Una línea de 1 px en el borde de una pieza de 24 px la
hace medir 25 px, y el marco entero se descuadra (esquinas separadas, huecos). → Las líneas de onda de los
menús son **formas rellenas de 1 px**, no trazos (`pieza_banda`). Para comprobar una pieza:

```bash
./v2/herramientas/prueba/medir-marco.sh v2/plasma/desktoptheme/OweeKoi-Onda/widgets/background.svg topleft top
```

**Plasma repite las piezas de borde si no le dices que las estire.** Sin el elemento `hint-stretch-borders`, el
calendario muestra marcas tipo regla en cada junta. Está en `svg_marco`; no lo quites.

**Pieza semitransparente = pieza que no se solapa.** Si el margen declarado (`hint-*-margin`) es menor que el
tamaño de la pieza, el centro se pinta dos veces bajo los bordes y se ve un recuadro. Por eso las piezas del
panel miden 8 px, igual que su margen.

**La sombra del menú va dentro del marco.** Plasma coloca la malla `shadow-*` fuera de la ventana; si la sombra
tiene el borde interior recto se ve un cuadrado a unos 36 px del menú. Por eso OweeKoi la pone en el anillo
transparente del propio marco, con el hueco redondeado, y deja `shadow-*` vacío en los menús.

## 2. Union (estilo de controles)

- Está marcado **"en desarrollo"** en Plasma 6.8. Es opcional y reversible (`owee-estilo`).
- El estilo se elige con la variable de entorno **`UNION_STYLE_NAME`**; la opción `--style` del inspector no
  lo hace. Las cachés se saltan con `UNION_DISABLE_STYLE_CACHE=1` (útil mientras editas el CSS).
- **Las reglas CSS se aplican por orden.** Una regla posterior pisa a una anterior aunque sea menos
  específica; por eso Breeze repite `:pressed` al final del archivo.
- **El estilo de Qt Widgets no pinta `box-shadow` ni `outline`** (lo comprobamos con una sombra roja
  exagerada), y solo admite bordes `solid` o `none`. Un halo exterior alrededor de los botones no es posible
  hoy; el rasgo de OweeKoi son la forma (cápsula) y el tinte de acento.
- **Un radio grande vuelve redondas las casillas** (16 px de indicador con radio 8 = círculo). Por eso existe
  `--small-radius`.
- Inspector de reglas: `union-ruleinspector --type Button` (con `UNION_STYLE_NAME=oweekoi`).

## 3. Colores de KDE

- **`ColorEffects:Disabled` e `Inactive` deben existir** en el esquema; si no, Plasma los deja vacíos en
  `kdeglobals` y los controles desactivados/inactivos salen mal.
- **El oscurecimiento de KDE conserva el tinte.** En un crema casi blanco `(255,253,247)` el efecto "oscurecer"
  da `(255,241,193)`, un amarillo. En claro se usa `IntensityEffect=0`.
- Plasma **no recarga un esquema con el mismo nombre**: pasa por otro y vuelve (`plasma-apply-colorscheme`).
- Un esquema se comprueba sin tocar tu sesión con una configuración temporal
  (`XDG_CONFIG_HOME=/tmp/x` con un `kdeglobals` que solo tenga el esquema) y una pequeña aplicación Qt que
  imprima `QApplication::palette()`; ver `herramientas/prueba/`.

## 4. Iconos y cursores

- **`FollowsColorScheme=true`** en el `index.theme` hace que KDE recolore los iconos monocromos de Breeze; sin
  él salen oscuros sobre el modo oscuro.
- Dolphin pide iconos de carpeta **por nombre** (`folder-android`, `folder-qt`…). Los nombres que el tema no
  define caen a otro estilo o a uno genérico. Un archivo `~/.local/share/mime/packages/inode-directory.xml`
  que cambie el icono de "Folder" afecta a **todas** las carpetas sin icono propio.
- Un cursor **animado** es un archivo Xcursor con varios fotogramas por tamaño. `libXcursor` carga lo que
  `xcursorgen` produce; se puede validar con `XcursorFilenameLoadAllImages` desde Python (`ctypes`).
- Al desplazar una sombra con `ImageChops.offset` el borde se **enrolla** (aparece arriba lo de abajo):
  usa `paste` sobre una imagen vacía.

## 4b. Login

El **Plasma Login Manager** (`plasmalogin`) no usa temas de SDDM. Su pantalla va compilada; se personaliza el
fondo (solo tipos estándar: Image, Plain Color, Tiled, Hunyango, Haenau, Picture of the Day), y los colores,
estilo, iconos y cursor se **sincronizan** desde tu configuración al usuario `plasmalogin`. Ese usuario no lee tu
carpeta personal: todo lo que use tiene que estar en `/usr/share`.

## 5. Plasma: temas globales y paneles

- Un tema global **sin `layouts`** o con una sección `[Wallpaper]` en `defaults` puede **reiniciar tus paneles**
  al aplicarse. OweeKoi trae su propia disposición y no usa `[Wallpaper]`.
- Según su ayuda, `lookandfeeltool -a <tema>` solo reinicia la disposición con `--resetLayout`; en este equipo se
  reinició igualmente con un tema sin `layouts` y con `[Wallpaper]`. Guarda siempre antes una copia de
  `plasma-org.kde.plasma.desktop-appletsrc`.
- Los scripts de disposición se ejecutan con `qdbus6 org.kde.plasmashell /PlasmaShell …evaluateScript`; se pueden
  probar en seco (crean un panel que luego borras con `panel.remove()`).

## 6. Fallo de dconf al cambiar ajustes de GTK

Al cambiar el icono o el cursor, `kde-gtk-config` reescribe los ajustes de GTK en dconf. En Ubuntu 24.04
(dconf 0.40) eso hizo caer a la vez `xdg-desktop-portal-gtk`, VS Code, Chromium y Electron, con la misma pila:
`libdconfsettings.so` llamando a una dirección nula. Cambiar solo claro/oscuro no lo provocó. Mitigación: aplicar
el tema con esas aplicaciones cerradas. Una opción más drástica es desactivar el módulo `gtkconfig` de `kded6`
(las apps GTK dejan de seguir el tema en vivo).

## 7. Diagnóstico

| Quieres saber… | Comando |
|---|---|
| Qué cambió un ajuste y cuándo | `ls -la --time-style=full-iso ~/.config/kdeglobals ~/.config/kcminputrc` |
| Qué se cayó | `coredumpctl list --since today` · `coredumpctl info <pid>` |
| Qué icono resuelve KDE | `kiconfinder6 folder-android` |
| Qué icono ve GIO para una carpeta | `gio info -a standard::icon ~/Dev` |
| Efectos de KWin activos | `qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadedEffects` |
| Paneles y widgets reales | `qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'panels().forEach(...)'` |
| Quién usa inotify | `for p in /proc/[0-9]*; do ls -l $p/fd 2>/dev/null \| grep -c inotify; done` |
| Qué registra el sistema | `journalctl --user --since "10 min ago"` |
