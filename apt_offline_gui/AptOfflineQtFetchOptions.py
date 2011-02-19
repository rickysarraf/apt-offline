import sys
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtFetchOptions import Ui_downloadOptionsDialog

class AptOfflineQtFetchOptions(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_downloadOptionsDialog()
        self.ui.setupUi(self)
        

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtFetchOptions()
    myapp.show()
    sys.exit(app.exec_())
