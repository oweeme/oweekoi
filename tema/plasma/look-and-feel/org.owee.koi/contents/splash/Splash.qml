import QtQuick

// Pantalla de inicio: el logo respira en el centro y dos kois nadan a su alrededor.
Rectangle {
    id: root
    color: "#0f3d34"

    property int stage

    Image {
        anchors.fill: parent
        source: "images/agua.jpg"
        fillMode: Image.PreserveAspectCrop
    }

    // anillo que se expande bajo el logo
    Repeater {
        model: 2
        Rectangle {
            id: anillo
            required property int index
            anchors.centerIn: parent
            width: logo.width
            height: width
            radius: width / 2
            color: "transparent"
            border.color: "#ffffff"
            border.width: 2
            opacity: 0
            SequentialAnimation {
                running: true
                loops: Animation.Infinite
                PauseAnimation { duration: anillo.index * 1600 }
                ParallelAnimation {
                    NumberAnimation { target: anillo; property: "width"; from: logo.width; to: logo.width * 2.6; duration: 3200; easing.type: Easing.OutQuad }
                    SequentialAnimation {
                        NumberAnimation { target: anillo; property: "opacity"; from: 0; to: 0.28; duration: 400 }
                        NumberAnimation { target: anillo; property: "opacity"; to: 0; duration: 2800 }
                    }
                }
            }
        }
    }

    Image {
        id: logo
        anchors.centerIn: parent
        width: Math.min(root.width, root.height) * 0.26
        height: width
        source: "images/logo.png"
        smooth: true
        opacity: 0
        scale: 0.9
        NumberAnimation on opacity { from: 0; to: 1; duration: 600; running: true }
        SequentialAnimation on scale {
            running: true
            loops: Animation.Infinite
            NumberAnimation { to: 1.04; duration: 2200; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0.97; duration: 2200; easing.type: Easing.InOutSine }
        }
    }

    component Pez: Item {
        id: pez
        property url hoja
        property int fw: 438
        property int fh: 275
        property int cabezaX: 124
        property int cabezaY: 139
        property real radioFinal: 0.30
        property real radio: radioFinal
        property int sentido: -1
        property real fase: 0
        property int periodo: 7
        property real escala: 0.17

        x: root.width / 2
        y: root.height / 2

        NumberAnimation on radio {
            from: 0.75; to: pez.radioFinal; duration: 2400; easing.type: Easing.OutCubic
        }

        Item {
            NumberAnimation on rotation {
                from: pez.fase
                to: pez.fase + pez.sentido * 360
                duration: pez.periodo * 1000
                loops: Animation.Infinite
                running: true
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
                    frameDuration: 70
                    loops: AnimatedSprite.Infinite
                    running: true
                    smooth: true
                    width: pez.escala * root.width
                    height: width * pez.fh / pez.fw
                    x: -(pez.cabezaX + 85) * s
                    y: -pez.cabezaY * s
                }
            }
        }
    }

    Pez { hoja: "images/koi-kohaku.png"; fh: 275; cabezaY: 139; sentido: -1; fase: 30; periodo: 7 }
    Pez { hoja: "images/koi-showa.png"; fh: 274; cabezaY: 136; sentido: -1; fase: 210; periodo: 7; radioFinal: 0.27 }
}
