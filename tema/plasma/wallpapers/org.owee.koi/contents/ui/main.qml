import QtQuick
import org.kde.plasma.plasmoid

// Estanque con kois: los peces son hojas de sprites con la ondulacion ya dibujada,
// y solo se mueven con transformaciones de GPU (consumo muy bajo).
WallpaperItem {
    id: root

    Rectangle { anchors.fill: parent; color: "#0f3d34" }
    Image {
        anchors.fill: parent
        source: Qt.resolvedUrl("../images/agua.jpg")
        fillMode: Image.PreserveAspectCrop
        smooth: true
    }

    component Pez: Item {
        id: pez
        property url hoja
        property int fw
        property int fh
        property int cabezaX      // posicion de la cabeza dentro del cuadro
        property int cabezaY
        property real escala: 0.3 // ancho en pantalla = escala * ancho de la pantalla
        property real cx: 0.5     // centro de la orbita (fraccion de la pantalla)
        property real cy: 0.5
        property real radio: 0.3  // fraccion del alto
        property int sentido: -1  // -1 antihorario, 1 horario
        property real fase: 0
        property int periodo: 80  // segundos por vuelta
        property real deriva: 0.06

        x: root.width * cx
        y: root.height * cy

        SequentialAnimation on x {
            running: root.visible
            loops: Animation.Infinite
            NumberAnimation { to: root.width * (pez.cx + pez.deriva); duration: pez.periodo * 420; easing.type: Easing.InOutSine }
            NumberAnimation { to: root.width * (pez.cx - pez.deriva); duration: pez.periodo * 420; easing.type: Easing.InOutSine }
        }

        Item {
            id: giro
            NumberAnimation on rotation {
                from: pez.fase
                to: pez.fase + pez.sentido * 360
                duration: pez.periodo * 1000
                loops: Animation.Infinite
                running: root.visible
            }
            Item {
                x: pez.radio * root.height
                rotation: -pez.sentido * 90
                AnimatedSprite {
                    readonly property real s: width / pez.fw
                    source: pez.hoja
                    frameWidth: pez.fw
                    frameHeight: pez.fh
                    frameCount: 16
                    frameDuration: 80
                    loops: AnimatedSprite.Infinite
                    running: root.visible
                    interpolate: false
                    smooth: true
                    width: pez.escala * root.width
                    height: width * pez.fh / pez.fw
                    x: -(pez.cabezaX + 170) * s
                    y: -pez.cabezaY * s
                }
            }
        }
    }

    Pez {
        hoja: Qt.resolvedUrl("../images/koi-kohaku.png")
        fw: 876; fh: 550; cabezaX: 249; cabezaY: 278
        cx: 0.36; cy: 0.5; radio: 0.30; sentido: -1; fase: 20; periodo: 70
    }
    Pez {
        hoja: Qt.resolvedUrl("../images/koi-showa.png")
        fw: 876; fh: 549; cabezaX: 249; cabezaY: 273
        cx: 0.64; cy: 0.5; radio: 0.26; sentido: 1; fase: 200; periodo: 86
    }
    Pez {
        hoja: Qt.resolvedUrl("../images/koi-ogon.png")
        fw: 876; fh: 548; cabezaX: 249; cabezaY: 275
        escala: 0.24
        cx: 0.5; cy: 0.54; radio: 0.42; sentido: -1; fase: 110; periodo: 118
    }
}
