#!/usr/bin/env python
from qt import *
from pyptofflinegui import pyptofflineguiForm


if __name__ == "__main__":
    import sys
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = pyptofflineguiForm()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
