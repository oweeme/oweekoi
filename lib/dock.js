// Dock flotante inferior que se oculta cuando una ventana lo tapa.
// install.sh sustituye __LANZADORES__ por la lista de aplicaciones instaladas.
var lanzadores = __LANZADORES__;

var dock = null;
panels().forEach(function (p) {
    if (p.location == "bottom" && p.hiding == "dodgewindows") {
        p.widgetIds.forEach(function (id) {
            var w = p.widgetById(id);
            if (w.type == "org.kde.plasma.icontasks") {
                dock = w;
            }
        });
    }
});

if (dock === null) {
    var p = new Panel;
    p.location = "bottom";
    p.height = 60;
    p.alignment = "center";
    p.lengthMode = "fit";
    p.floating = true;
    p.hiding = "dodgewindows";
    dock = p.addWidget("org.kde.plasma.icontasks");
    dock.currentConfigGroup = ["General"];
    dock.writeConfig("iconSpacing", 2);
}
dock.currentConfigGroup = ["General"];
dock.writeConfig("launchers", lanzadores);
