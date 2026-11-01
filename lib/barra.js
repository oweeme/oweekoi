// Barra superior estilo macOS: menu de aplicaciones y escritorios a la izquierda,
// menu global de la aplicacion activa, reloj centrado y bandeja a la derecha.
// Quita el gestor de tareas de la barra superior (los iconos de apps viven en el dock).
// Imprime "PANEL=<id> ORDER=<ids>" para que install.sh fije el orden de los widgets.
var top = panels().filter(function (p) { return p.location == "top"; })[0];

if (!top) {
    print("NOPANEL");
} else {
    var tipos = {};
    var ids = [];
    top.widgetIds.forEach(function (id) {
        var tipo = top.widgetById(id).type;
        if (tipo == "org.kde.plasma.icontasks") {
            top.widgetById(id).remove();
        } else {
            ids.push(id);
            (tipos[tipo] = tipos[tipo] || []).push(id);
        }
    });

    function asegurar(tipo, cuantos) {
        while ((tipos[tipo] || []).length < cuantos) {
            var w = top.addWidget(tipo);
            ids.push(w.id);
            (tipos[tipo] = tipos[tipo] || []).push(w.id);
        }
    }
    asegurar("org.kde.plasma.appmenu", 1);
    asegurar("org.kde.plasma.panelspacer", 2);

    function uno(tipo, n) { return (tipos[tipo] || [])[n || 0]; }
    var orden = [
        uno("org.kde.plasma.kickoff"),
        uno("org.kde.plasma.pager"),
        uno("org.kde.plasma.appmenu"),
        uno("org.kde.plasma.panelspacer", 0),
        uno("org.kde.plasma.digitalclock"),
        uno("org.kde.plasma.panelspacer", 1),
        uno("org.kde.plasma.marginsseparator"),
        uno("org.kde.plasma.systemtray"),
        uno("org.kde.plasma.showdesktop")
    ].filter(function (id) { return id !== undefined; });
    ids.forEach(function (id) {
        if (orden.indexOf(id) < 0) { orden.push(id); }
    });
    print("PANEL=" + top.id + " ORDER=" + orden.join(";"));
}
