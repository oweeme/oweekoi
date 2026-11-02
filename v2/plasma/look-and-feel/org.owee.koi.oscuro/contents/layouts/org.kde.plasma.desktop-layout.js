// OweeKoi: barra superior con el menu global y el reloj centrado. Sin dock.
// Plasma ejecuta esto al aplicar el tema; reconstruye siempre la misma disposicion.
var panel = new Panel;
panel.location = "top";
panel.height = 30;
panel.floating = true;
panel.hiding = "none";

var kickoff = panel.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["Shortcuts"];
kickoff.writeConfig("global", "Alt+F1");
panel.addWidget("org.kde.plasma.pager");
panel.addWidget("org.kde.plasma.appmenu");
panel.addWidget("org.kde.plasma.panelspacer");
panel.addWidget("org.kde.plasma.digitalclock");
panel.addWidget("org.kde.plasma.panelspacer");
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.showdesktop");

// Fondo: el del usuario si esta instalado ahi, si no el del sistema
var fondo = userDataPath("data") + "/wallpapers/OweeKoi-Estanque";
if (!fileExists(fondo)) { fondo = "/usr/share/wallpapers/OweeKoi-Estanque"; }
var escritorios = desktopsForActivity(currentActivity());
for (var i = 0; i < escritorios.length; i++) {
    escritorios[i].wallpaperPlugin = "org.kde.image";
    escritorios[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    escritorios[i].writeConfig("Image", "file://" + fondo);
}
