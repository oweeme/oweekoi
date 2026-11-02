// Dibuja los controles de Qt Widgets con el estilo indicado y guarda una imagen.
#include <QApplication>
#include <QWidget>
#include <QGridLayout>
#include <QPushButton>
#include <QCheckBox>
#include <QRadioButton>
#include <QSlider>
#include <QProgressBar>
#include <QComboBox>
#include <QLineEdit>
#include <QSpinBox>
#include <QTabBar>
#include <QTabWidget>
#include <QGroupBox>
#include <QToolButton>
#include <QScrollBar>
#include <QListWidget>
#include <QLabel>
#include <QTimer>
#include <QPixmap>
#include <QDebug>

int main(int argc, char **argv) {
    QApplication app(argc, argv);
    QString salida = argc > 1 ? argv[1] : "galeria.png";
    qInfo() << "estilo en uso:" << app.style()->objectName();
    QWidget w; w.resize(760, 520);
    auto *g = new QGridLayout(&w);
    auto *normal = new QPushButton("Aceptar");
    auto *def = new QPushButton("Por defecto"); def->setDefault(true);
    auto *off = new QPushButton("Desactivado"); off->setEnabled(false);
    auto *chk = new QPushButton("Marcado"); chk->setCheckable(true); chk->setChecked(true);
    g->addWidget(normal, 0, 0); g->addWidget(def, 0, 1); g->addWidget(off, 0, 2); g->addWidget(chk, 0, 3);
    auto *c1 = new QCheckBox("Casilla"); c1->setChecked(true);
    auto *c2 = new QCheckBox("Sin marcar");
    auto *c3 = new QCheckBox("Intermedia"); c3->setTristate(true); c3->setCheckState(Qt::PartiallyChecked);
    auto *r1 = new QRadioButton("Opcion A"); r1->setChecked(true);
    g->addWidget(c1, 1, 0); g->addWidget(c2, 1, 1); g->addWidget(c3, 1, 2); g->addWidget(r1, 1, 3);
    auto *r2 = new QRadioButton("Opcion B");
    auto *sl = new QSlider(Qt::Horizontal); sl->setValue(40);
    auto *pb = new QProgressBar; pb->setValue(65);
    g->addWidget(r2, 2, 0); g->addWidget(sl, 2, 1, 1, 2); g->addWidget(pb, 2, 3);
    auto *cb = new QComboBox; cb->addItems({"Tinta", "Papel", "Estanque"});
    auto *le = new QLineEdit("Texto de ejemplo");
    auto *sp = new QSpinBox; sp->setValue(12);
    auto *tb = new QToolButton; tb->setText("Herramienta");
    g->addWidget(cb, 3, 0); g->addWidget(le, 3, 1, 1, 2); g->addWidget(sp, 3, 3);
    auto *tabs = new QTabWidget; tabs->addTab(new QLabel("Contenido de la primera pestana"), "General");
    tabs->addTab(new QLabel("Dos"), "Apariencia"); tabs->addTab(new QLabel("Tres"), "Avanzado");
    auto *lista = new QListWidget; lista->addItems({"Documentos", "Descargas", "Musica", "Imagenes"}); lista->setCurrentRow(1);
    auto *grupo = new QGroupBox("Grupo"); auto *gl = new QGridLayout(grupo); gl->addWidget(tb, 0, 0); gl->addWidget(new QScrollBar(Qt::Horizontal), 1, 0);
    g->addWidget(tabs, 4, 0, 1, 2); g->addWidget(lista, 4, 2); g->addWidget(grupo, 4, 3);
    w.show();
    QTimer::singleShot(900, [&]() { w.grab().save(salida); qInfo() << "guardado" << salida; app.quit(); });
    return app.exec();
}
