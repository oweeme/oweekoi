// Pide al estilo actual que dibuje cada control en cada estado (reposo, raton encima, foco, pulsado, marcado, desactivado).
#include <QApplication>
#include <QStyle>
#include <QStyleOption>
#include <QPainter>
#include <QImage>
#include <QPalette>
#include <QDebug>
int main(int argc, char **argv) {
    QApplication app(argc, argv);
    QString salida = argc > 1 ? argv[1] : "estados.png";
    struct Est { const char *n; QStyle::State s; };
    const QStyle::State base = QStyle::State_Enabled | QStyle::State_Active;
    QList<Est> estados = {
        {"reposo", base},
        {"raton encima", base | QStyle::State_MouseOver},
        {"foco", base | QStyle::State_HasFocus | QStyle::State_KeyboardFocusChange},
        {"pulsado", base | QStyle::State_Sunken | QStyle::State_MouseOver},
        {"marcado", base | QStyle::State_On},
        {"desactivado", QStyle::State_None | QStyle::State_Active},
    };
    const int cw = 150, ch = 54, filas = 5;
    QImage img(cw * estados.size() + 10, ch * filas + 10, QImage::Format_ARGB32_Premultiplied);
    img.fill(QApplication::palette().color(QPalette::Window));
    QPainter p(&img);
    p.setPen(QApplication::palette().color(QPalette::WindowText));
    QStyle *st = app.style();
    for (int c = 0; c < estados.size(); ++c) {
        int x = 5 + c * cw;
        QRect r(x + 12, 5 + 12, cw - 24, 30);
        // fila 0: boton
        QStyleOptionButton b; b.fontMetrics = app.fontMetrics(); b.rect = r; b.state = estados[c].s; b.text = estados[c].n; b.palette = QApplication::palette();
        st->drawControl(QStyle::CE_PushButton, &b, &p);
        // fila 1: casilla
        QStyleOptionButton k = b; k.rect = QRect(x + 12, 5 + ch + 12, cw - 24, 30); k.text = "casilla";
        k.state = estados[c].s | (estados[c].s & QStyle::State_On ? QStyle::State_None : QStyle::State_None);
        if (!(k.state & QStyle::State_On)) k.state |= QStyle::State_Off;
        st->drawControl(QStyle::CE_CheckBox, &k, &p);
        // fila 2: radio
        QStyleOptionButton ro = k; ro.rect = QRect(x + 12, 5 + 2 * ch + 12, cw - 24, 30); ro.text = "radio";
        st->drawControl(QStyle::CE_RadioButton, &ro, &p);
        // fila 3: campo de texto
        QStyleOptionFrame f; f.fontMetrics = app.fontMetrics(); f.rect = QRect(x + 12, 5 + 3 * ch + 12, cw - 24, 28); f.state = estados[c].s; f.lineWidth = 1; f.palette = QApplication::palette(); f.features = QStyleOptionFrame::None;
        st->drawPrimitive(QStyle::PE_PanelLineEdit, &f, &p);
        p.drawText(f.rect.adjusted(8, 0, 0, 0), Qt::AlignVCenter, "texto");
        // fila 4: boton plano de herramienta
        QStyleOptionToolButton t; t.fontMetrics = app.fontMetrics(); t.rect = QRect(x + 12, 5 + 4 * ch + 12, cw - 24, 30); t.state = estados[c].s | QStyle::State_AutoRaise; t.text = "herramienta"; t.toolButtonStyle = Qt::ToolButtonTextOnly; t.palette = QApplication::palette();
        st->drawComplexControl(QStyle::CC_ToolButton, &t, &p);
        st->drawControl(QStyle::CE_ToolButtonLabel, &t, &p);
    }
    p.end();
    img.save(salida);
    qInfo() << "estilo:" << st->objectName() << "->" << salida;
    return 0;
}
