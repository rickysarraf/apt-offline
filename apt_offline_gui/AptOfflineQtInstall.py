import sys
from PyQt4 import QtCore, QtGui

from Ui_AptOfflineQtInstall import Ui_AptOfflineQtInstall


class AptOfflineQtInstall(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineQtInstall()
        self.ui.setupUi(self)
        
        # Connect the clicked signal of the Browse button to it's slot
        QtCore.QObject.connect(self.ui.browseFilePathButton, QtCore.SIGNAL("clicked()"),
                        self.popupDirectoryDialog )
                        
        # Connect the clicked signal of the Save to it's Slot - accept
        QtCore.QObject.connect(self.ui.startInstallButton, QtCore.SIGNAL("clicked()"),
                        self.StartInstall )
                        
        # Connect the clicked signal of the Cancel to it's Slot - reject
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"),
                        self.reject )
        
        QtCore.QObject.connect(self.ui.zipFilePath, QtCore.SIGNAL("editingFinished()"),
                        self.ControlStartInstallBox )
        
    def StartInstall(self):
        self.accept()

    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtGui.QFileDialog.getOpenFileName(self, u'Select the Zip File')
        # Show the selected file path in the field marked for showing directory path
        self.ui.zipFilePath.setText(directory)
        self.ui.zipFilePath.setFocus()
    
    def ControlStartInstallBox(self):
        if self.ui.zipFilePath.text().isEmpty():
            self.ui.startInstallButton.setEnabled(False)
        else:
            self.ui.startInstallButton.setEnabled(True)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtInstall()
    myapp.show()
    sys.exit(app.exec_())
