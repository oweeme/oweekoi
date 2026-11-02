# OweeKoi 2 — Manual para modificarlo a mano

Este manual explica cómo cambiar cualquier parte de OweeKoi 2 tú mismo: qué archivo editar, qué comando
ejecutar y cómo ver el resultado sin romper nada. Las trampas técnicas (lo que falló y por qué) están en
[NOTAS-TECNICAS.md](NOTAS-TECNICAS.md); léelas antes de tocar las piezas gráficas.

## 1. Cómo funciona, en un minuto

```
 paleta.py ─┐
            ├─►  generadores  ─►  archivos del tema  ─►  instalar.sh  ─►  tu carpeta personal
 (colores)  │   herramientas/     colores/ iconos/ …     (respalda y      ~/.local/share, ~/.config
            │   generar_*.py                              aplica)
            └──────────── ./v2/regenerar.sh ────────────┘
```

**Regla de oro:** los archivos *generados* no se editan a mano, porque se pisan al regenerar. Se edita la
paleta o el generador y se ejecuta `./v2/regenerar.sh`.

Lo que **sí** se edita a mano (no se regenera): el estilo de controles `estilo/oweekoi/contents/css/*.css`,
los scripts `herramientas/owee-*`, `integracion/`, `instalar.sh`, `desinstalar.sh` y `login/`.

## 2. Receta rápida

| Quiero cambiar… | Edito | Luego ejecuto |
|---|---|---|
| Un color (fondo, acento, texto…) de claro u oscuro | `herramientas/paleta.py` (diccionarios `OSCURO` y `CLARO`) | `./v2/regenerar.sh` · `./v2/instalar.sh` |
| El color o la saturación de las carpetas | `paleta.py` → `CARPETAS` (tonos), `L_CARPETA`, `C_CARPETA` | `./v2/regenerar.sh carpetas` |
| Qué símbolo lleva una carpeta, o añadir una | `herramientas/generar_carpetas.py` → `USO`, `GRUPOS`, `SIMBOLOS`, `GLIFOS` | `./v2/regenerar.sh carpetas` |
| El radio de las esquinas de los botones | `estilo/oweekoi/contents/css/variables.css` → `--button-radius` | `./v2/herramientas/prueba/probar-estilo.sh` |
| El radio de campos de texto y listas | mismo archivo → `--corner-radius` (casillas: `--small-radius`) | ídem |
| El tinte al pasar el ratón sobre un botón | `estilo/oweekoi/contents/css/button.css` → `--onda-tinte` (la mezcla, 0.14) | ídem |
| La forma o el color de la flecha del cursor | `herramientas/generar_punteros.py` → `FLECHA`, `CREMA`, `TINTA`, `CORAL` | `./v2/regenerar.sh punteros` |
| El agua, las ondas o las hojas del fondo | `herramientas/generar_fondos.py` → `MODOS`, `ONDAS`, `HOJAS`, `KOIS` | `./v2/regenerar.sh fondos` |
| Cómo nadan los kois del protector | `plasma/wallpapers/org.owee.koi/contents/ui/main.qml` (bloques `Pez {…}`) | `./v2/instalar.sh` |
| Las esquinas, la sombra o los botones de las ventanas | `herramientas/generar_onda.py` → `R`, `SH_*`, `COLORES`, `GLIFOS` | `./v2/regenerar.sh ventanas` |
| Menús, calendario y barra: esquinas, halo de ondas | `herramientas/generar_plasma.py` → llamadas a `svg_marco(...)` al final | `./v2/regenerar.sh plasma` |
| La barra superior (qué widgets, altura, flotante) | `herramientas/generar_temas_globales.py` → `LAYOUT` | `./v2/regenerar.sh globales` |
| Velocidad y efectos de las animaciones | `herramientas/owee-animaciones` → `FACTOR` y los efectos | `owee-animaciones activar` |
| A qué hora cambia claro/oscuro | `~/.config/oweekoi/horario.conf` (`AMANECER`, `ANOCHECER`) | `owee-tema estado` |
| Colores de Konsole, Kate o Qt Creator | `herramientas/generar_editores.py` → `SINTAXIS` | `./v2/regenerar.sh editores` |

Después de regenerar, instala con `./v2/instalar.sh` y recarga la pieza (sección 5).

## 3. Antes de tocar nada

- **Tu configuración se respalda sola** en `~/.local/share/oweekoi/respaldo-v2-<fecha>` antes de aplicar. Para
  volver atrás: `./v2/desinstalar.sh` (restaura el último respaldo).
- **Prueba sin riesgo.** Para el estilo de controles: `./v2/herramientas/prueba/probar-estilo.sh` dibuja los
  controles en claro y oscuro en imágenes, sin instalar nada. Para verlos en una aplicación real:
  `owee-estilo probar kcalc`.
- **No cambies de tema con aplicaciones abiertas** (navegadores, VS Code, Claude): un fallo de dconf en
  Ubuntu 24.04 las cierra de golpe al cambiar los ajustes de GTK. Guarda tu trabajo y ciérralas primero.
- **Un solo commit por pieza** y la rama `v2`: así puedes deshacer una pieza sin perder las demás.

## 4. Las piezas, una por una

### 4.1 Paleta y colores — `herramientas/paleta.py`
Es la **fuente única de colores**: todo lo demás parte de aquí. Cada modo tiene estas claves:
`base` (fondo de ventana), `vista` (fondo de áreas de texto), `superficie` (barras de título, cabeceras),
`elevado` (botones), `borde`, `texto`, `suave` (texto secundario), `acento` (bordes y rellenos de foco),
`seleccion` y `sobre_seleccion` (lo seleccionado y su texto), `coral`, `positivo`, `neutro`, `enlace`, `visitado`.

- El filtro de calidad: `generar_colores.py` avisa **"BAJO CONTRASTE"** si un texto baja de 4,5:1 (WCAG AA).
- Los esquemas de KDE se generan en `colores/OweeKoiDark.colors` y `OweeKoiLight.colors`. Incluyen
  `ColorEffects` (cómo se ven los controles desactivados). En claro el oscurecimiento está desactivado a
  propósito: sobre un crema casi blanco KDE lo vuelve amarillo (ver notas técnicas).

### 4.2 Carpetas de colores — `generar_carpetas.py`
Genera el tema de iconos `OweeKoi` (hereda de Breeze): 129 iconos de carpeta mate (9 de ellos lisos,
`folder-owee-<color>`, para ponérselos a mano con el menú de Dolphin) y el logo de Owee en 9 tamaños.
- `USO` asigna color y símbolo a las carpetas del sistema (Documentos, Descargas…).
- `GRUPOS` reparte el resto de nombres `folder-<nombre>` que KDE puede pedir por color.
- Para añadir un símbolo: agrega un trazo SVG a `GLIFOS` y úsalo en `SIMBOLOS` o `USO`.
- `FollowsColorScheme=true` en el `index.theme` es **imprescindible**: sin él los iconos de Breeze salen
  oscuros sobre el modo oscuro.
- El menú de Dolphin (*Actions ▸ Color de carpeta*) escribe un archivo oculto `.directory` en la carpeta.

### 4.3 Punteros — `generar_punteros.py`
Crea el tema de cursores `OweeKoi-Punteros` (formato Xcursor, con `xcursorgen`). Solo redibuja cuatro:
`default` (flecha), `pointer` (flecha con anillo de onda), `wait` y `progress` (logo con ondas, animados).
El resto lo hereda de Breeze (`Inherits=breeze_cursors`). Tamaños: 24, 32, 48 y 64.
- Forma de la flecha: lista `FLECHA`, con la punta en (0, 0) y alto 1.
- Las animaciones usan 24 fotogramas de 50 ms; el logo sale de `tema/iconos/256/oweelogo.png`.
- Los alias (`left_ptr`, `hand2`, `watch`…) están en `ALIAS`: son enlaces a los cuatro reales.

### 4.4 Fondos y protector — `generar_fondos.py`
- El **fondo del escritorio** (`fondos/OweeKoi-Estanque`) lleva dos imágenes: `contents/images` (claro) y
  `contents/images_dark` (oscuro). Plasma elige solo según el modo.
- `MODOS` define los colores del agua de cada modo; `ONDAS` y `HOJAS` colocan anillos y hojas de loto
  (posición como fracción de la pantalla); `KOIS` coloca los peces: hoja de sprites, fotograma, posición,
  rumbo en grados y escala.
- Todo es determinista (semilla fija): el mismo comando da siempre la misma imagen.
- El **protector animado** es el plugin `plasma/wallpapers/org.owee.koi`. Elige `agua-claro.jpg` o
  `agua-oscuro.jpg` según el esquema activo. Los kois son tres hojas de 16 fotogramas; sus órbitas se
  ajustan en `main.qml` (`cx`, `cy`, `radio`, `sentido`, `fase`, `periodo`).
- El bloqueo salta a los 5 minutos: `kscreenlockerrc` → `[Daemon] Timeout`.

### 4.5 Ventanas "Onda" — `generar_onda.py`
Decorado de ventanas (Aurorae) propio, claro y oscuro.
- **Geometría** (constantes al inicio): `SH_T/L/R/B` sombra por lado, `R` radio de esquina, `TITULO` alto de
  la barra, `CHIN` el borde inferior donde se dibujan las esquinas de abajo. Si cambias alguna, cambia
  también `PaddingTop/Bottom/Left/Right` en la función `rc()`: tienen que coincidir.
- **Botones**: `COLORES` (cierre, minimizar, maximizar…), `GLIFOS` (el símbolo de cada uno) y `ESTADOS`.
- Las 9 piezas del marco se generan como **imágenes PNG incrustadas a doble resolución** (no como vectores):
  es a propósito, ver notas técnicas.
- Posición de los botones: no es del tema, es de KDE (*Decoración de ventanas ▸ Configurar botones*).

### 4.6 Estilo de Plasma — `generar_plasma.py`
Paneles, menús, calendario y diálogos (`plasma/desktoptheme/OweeKoi-Onda`). No lleva archivo de colores: **usa
los del esquema activo**, así sirve para claro y oscuro. Lo que no define lo toma Plasma de Breeze.
- Las llamadas finales a `svg_marco(S, E, I, R, margen, inset, S_sombra, opacidad, …)` definen cada marco:
  `S` tamaño de esquina, `E` largo del borde, `I` cuánto entra el cuerpo (inset), `R` radio, `margen` y
  `inset` (pistas para Plasma), `opacidad` (0.90 panel, 0.97 menús).
- El rasgo de OweeKoi: la **doble línea de onda** (`bandas`) y el **halo de tres anillos** alrededor de los menús
  (`-3, -6, -9` px). Para quitarlos, deja `bandas` con una sola línea y vacía el bucle del halo en `conjunto()`.

### 4.7 Estilo de controles — `estilo/oweekoi/` (CSS, se edita a mano)
Botones, campos, casillas, listas, pestañas. Usa **Union**, el motor de estilos nuevo de KDE, que sigue en
desarrollo en Plasma 6.8. Es un derivado del estilo Breeze (BSD-2-Clause, con crédito).
- `variables.css`: `--corner-radius` (8px), `--button-radius` (16px = cápsula), `--small-radius` (4px).
- `button.css`: `--onda-tinte` mezcla el color de acento al pasar el ratón o enfocar.
- Las reglas se aplican **por orden**, no por especificidad: una regla posterior pisa a una anterior.
- Ciclo de prueba: edita el CSS → `./v2/herramientas/prueba/probar-estilo.sh` → mira las imágenes.
- Se activa con `owee-estilo activar` (cierra sesión) y se quita con `owee-estilo desactivar`.

### 4.8 Temas globales y disposición — `generar_temas_globales.py`
Genera `OweeKoi Oscuro` y `OweeKoi Claro` (los que ves en *Temas globales*).
- `DEFAULTS` lista qué se aplica: esquema, iconos, cursor, estilo de Plasma, ventanas, pantalla de inicio y
  protector, animaciones. Es el formato de KDE: `[archivo][grupo]` y `clave=valor`.
- `LAYOUT` es el script que reconstruye la barra superior (kickoff, escritorios, menú global, reloj centrado,
  bandeja). Solo se ejecuta si marcas *"Desktop and window layout"* al aplicar el tema. **No pongas una línea
  `[Wallpaper]` en `DEFAULTS`**: reiniciaba tus paneles.
- Para añadir un dock, agrega otro `new Panel` al final de `LAYOUT`.

### 4.9 Animaciones — `herramientas/owee-animaciones`
Usa solo efectos que KWin ya trae: Magic Lamp al minimizar y todo un 20 % más lento (`FACTOR=1.2`).
`owee-animaciones activar` guarda tu estado anterior y `restaurar` lo devuelve. Otros efectos disponibles:
`qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.listOfEffects`.

### 4.10 Claro/oscuro — `owee-tema`
`owee-tema claro | oscuro | alternar | auto | estado`. `auto` usa `~/.config/oweekoi/horario.conf`:

```
AMANECER=07:00
ANOCHECER=19:00
```
Cambia también las ventanas Onda. La opción `./v2/instalar.sh --horario` activa un temporizador de usuario que lo
ejecuta cada 10 minutos. El interruptor *"Switch to Dark Mode at Night"* de KDE también funciona con los
temas globales, pero cada cambio puede cerrar aplicaciones GTK (sección 3).

### 4.11 Konsole, Kate y Qt Creator — `generar_editores.py`
`SINTAXIS` define los colores de sintaxis de cada modo. El script los **acerca al texto hasta cumplir 4,5:1**
contra el fondo. Salidas: `editores/konsole/*.colorscheme`, `editores/kate/*.theme`, `editores/qtcreator/*.xml`.
Se eligen en *Configurar Kate ▸ Fuentes y colores*, en el perfil `OweeKoi` de Konsole y en *Preferencias ▸
Editor de texto* de Qt Creator.

### 4.12 Login — `login/instalar-login.sh`
El Plasma Login Manager **no admite temas**: solo fondos estándar, colores y estilo sincronizados.
1. `sudo ./v2/login/instalar-login.sh` copia el tema a `/usr/share` (el usuario del login no lee tu carpeta personal).
2. *Configuración del sistema ▸ Pantalla de inicio de sesión ▸ Configure Appearance*: tipo **Image** y elige
   **"OweeKoi - Estanque (login)"**.
3. *Apply Plasma Settings…* copia colores, estilo, iconos y cursor al login.
El fondo animado de kois no se puede usar ahí.

Para comprobar el tamaño de las piezas de un SVG de marco: `./v2/herramientas/prueba/medir-marco.sh <archivo.svg>`.

## 5. Ver los cambios (recargar cada pieza)

| Pieza | Cómo recargar |
|---|---|
| Colores | `plasma-apply-colorscheme OweeKoiLight` y luego `OweeKoiDark` (si aplicas el mismo nombre, no recarga) |
| Iconos | `/usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons breeze` y luego `OweeKoi` |
| Punteros | `plasma-apply-cursortheme OweeKoi-Punteros` (cierra antes las apps GTK/Electron) |
| Ventanas | `kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__OweeKoi-Onda-Dark` y `qdbus6 org.kde.KWin /KWin reconfigure` |
| Estilo de Plasma | `plasma-apply-desktoptheme default` y luego `OweeKoi-Onda` |
| Fondo | `plasma-apply-wallpaperimage ~/.local/share/wallpapers/OweeKoi-Estanque` |
| Protector | `Super+L`, o sin bloquear: `/usr/lib/x86_64-linux-gnu/libexec/kscreenlocker_greet --testing` |
| Estilo de controles | `owee-estilo probar kcalc` (una app) o cerrar sesión (todo el escritorio) |
| Temas de editor | reabrir Kate, Konsole o Qt Creator |

## 6. Si algo sale mal

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Se cierran navegadores, VS Code y Claude al cambiar de tema | Fallo de dconf al cambiar ajustes de GTK | Ciérralos antes; aplica el tema a mano |
| Aviso "Inotify Instance Capacity Low" | Límite de 128 de Ubuntu | `sudo sysctl fs.inotify.max_user_instances=1024` (el instalador lo deja fijo) |
| Los botones de ventana salen con bloques negros o la barra en "pestañas" | Se usó `clipPath` o trazos en un SVG de ventana | Notas técnicas, sección 1 |
| Calendario con marcas tipo regla en los bordes | Falta `hint-stretch-borders` en el SVG del menú | Está en `generar_plasma.py`; no lo quites |
| Controles desactivados amarillos en modo claro | El oscurecimiento de KDE conserva el tinte del crema | `IntensityEffect=0` en `generar_colores.py` |
| Carpetas con el icono de Qt Designer | Un archivo MIME de usuario cambió el icono de "Folder" | Borra `~/.local/share/mime/packages/inode-directory.xml` y `update-mime-database ~/.local/share/mime` |
| Se perdió tu barra o tu dock tras aplicar un tema | El tema trajo su propia disposición | Restaura `plasma-org.kde.plasma.desktop-appletsrc` de `~/.local/share/oweekoi/` |
| El estilo de controles se ve raro | Union está en desarrollo | `owee-estilo desactivar` y cierra sesión |
| El cursor volvió a Breeze | Algo lo reescribió | Elígelo en *Punteros*, con las aplicaciones cerradas |

## 7. Archivos que toca el instalador

**En tu carpeta personal** (con respaldo): `~/.local/share/{color-schemes, icons/OweeKoi, icons/OweeKoi-Punteros,
wallpapers/OweeKoi-Estanque, plasma/wallpapers/org.owee.koi, plasma/desktoptheme/OweeKoi-Onda,
plasma/look-and-feel/org.owee.koi*, aurorae/themes/OweeKoi-Onda-*, union/styles/oweekoi, kio/servicemenus,
konsole, org.kde.syntax-highlighting/themes}`, `~/.config/QtProject/qtcreator/styles` y `~/.local/bin/owee-*`.
Cambia los ajustes `kdeglobals`, `kcminputrc`, `plasmarc`, `kwinrc`, `ksplashrc`, `kscreenlockerrc` y la barra
superior en `plasma-org.kde.plasma.desktop-appletsrc`.

**En el sistema** (solo con `sudo ./v2/login/instalar-login.sh`): copias en `/usr/share` para el login.

## 8. Publicar tus cambios

```bash
git switch v2                       # trabaja en la rama v2; main queda como la v1
./v2/regenerar.sh && git status     # ¿qué cambió?
git add -A && git commit -m "v2: lo que cambiaste y por qué"
git push origin v2
```

## 9. Licencias y créditos

GPL-3.0 para el conjunto. El estilo de controles `estilo/oweekoi` es un derivado del estilo Breeze de Union
(BSD-2-Clause, Arjen Hiemstra y Akseli Lahtinen) y conserva esa licencia y su aviso. El logo y los kois son de Owee.
Ninguna pieza de OweeKoi 2 deriva de WhiteSur.
