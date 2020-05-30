import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from apt_offline_gui.Ui_AptOfflineQtAbout import Ui_AboutAptOffline


class AptOfflineQtAbout(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_AboutAptOffline()
        self.ui.setupUi(self)
        self.setupLicense()

    def setupLicense(self):
        ''' LICENSE is looked for in -
                1. Current directory (dev / possibly windows)
                2. /usr/local/share/doc/apt-offline (source install)
                3. /usr/share/doc/apt-offline (package install)

            TODO: to resolve location on window
        '''
        filename = 'LICENSE'
        locations = ['.', '/usr/local/share/doc/apt-offline/', '/usr/share/doc/apt-offline']
        for l in locations:
            filepath = os.path.join(l,filename)
            if os.path.isfile(filepath):
                f = open(filepath,"r")
                self.ui.licenseText.setPlainText(f.read())
                f.close()
                return

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtAbout()
    myapp.show()
    sys.exit(app.exec_())
