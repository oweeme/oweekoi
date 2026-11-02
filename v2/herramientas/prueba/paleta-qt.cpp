#include <QApplication>
#include <QPalette>
#include <QDebug>
static QString h(const QColor &c){ return QString("(%1,%2,%3)").arg(c.red()).arg(c.green()).arg(c.blue()); }
int main(int a, char **v){ QApplication app(a, v); QPalette p = QApplication::palette();
  qInfo().noquote() << "Button   activo:" << h(p.color(QPalette::Active,QPalette::Button)) << " desactivado:" << h(p.color(QPalette::Disabled,QPalette::Button)) << " inactivo:" << h(p.color(QPalette::Inactive,QPalette::Button));
  qInfo().noquote() << "Window   activo:" << h(p.color(QPalette::Active,QPalette::Window)) << " desactivado:" << h(p.color(QPalette::Disabled,QPalette::Window));
  qInfo().noquote() << "Base     activo:" << h(p.color(QPalette::Active,QPalette::Base)) << " desactivado:" << h(p.color(QPalette::Disabled,QPalette::Base));
  qInfo().noquote() << "Text     activo:" << h(p.color(QPalette::Active,QPalette::ButtonText)) << " desactivado:" << h(p.color(QPalette::Disabled,QPalette::ButtonText)); return 0; }
