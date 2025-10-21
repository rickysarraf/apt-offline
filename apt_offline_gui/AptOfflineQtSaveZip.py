import sys
from PyQt6 import QtCore, QtGui, QtWidgets

from apt_offline_gui.Ui_AptOfflineQtSaveZip import Ui_SaveZipFile


class AptOfflineQtSaveZip(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_SaveZipFile()
        self.ui.setupUi(self)

        # Connect the clicked signal of the Browse button to it's slot
        self.ui.browseFilePathButton.clicked.connect(self.popupDirectoryDialog)

        # Connect the clicked signal of the Save to it's Slot - accept
        self.ui.saveButton.clicked.connect(self.accept)

        # Connect the clicked signal of the Cancel to it's Slot - reject
        self.ui.cancelButton.clicked.connect(self.reject)

    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Directory')
        # Show the selected file path in the field marked for showing directory path
        self.ui.zipFilePath.setText(directory)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = AptOfflineQtSaveZip()
    myapp.show()
    sys.exit(app.exec())
