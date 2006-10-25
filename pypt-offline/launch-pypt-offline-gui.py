#!/usr/bin/env python
from qt import *
from pypt_offline_gui import Form1


if __name__ == "__main__":
    import sys
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = Form1()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
