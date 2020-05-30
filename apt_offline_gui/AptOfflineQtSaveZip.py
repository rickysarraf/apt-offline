import sys
from PyQt5 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtSaveZip import Ui_SaveZipFile


class AptOfflineQtSaveZip(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_SaveZipFile()
        self.ui.setupUi(self)

        # Connect the clicked signal of the Browse button to it's slot
        QtCore.QObject.connect(self.ui.browseFilePathButton, QtCore.SIGNAL("clicked()"),
                        self.popupDirectoryDialog )

        # Connect the clicked signal of the Save to it's Slot - accept
        QtCore.QObject.connect(self.ui.saveButton, QtCore.SIGNAL("clicked()"),
                        self.accept )

        # Connect the clicked signal of the Cancel to it's Slot - reject
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"),
                        self.reject )

    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory')
        # Show the selected file path in the field marked for showing directory path
        self.ui.zipFilePath.setText(directory)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtSaveZip()
    myapp.show()
    sys.exit(app.exec_())
