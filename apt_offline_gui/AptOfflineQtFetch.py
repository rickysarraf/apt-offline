import sys
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtFetch import Ui_AptOfflineQtFetch


class AptOfflineQtFetch(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineQtFetch()
        self.ui.setupUi(self)
        
        # Connect the clicked signal of the Browse button to it's slot
        QtCore.QObject.connect(self.ui.browseFilePathButton, QtCore.SIGNAL("clicked()"),
                        self.popupDirectoryDialog )
                        
        # Connect the clicked signal of the Save to it's Slot - accept
        QtCore.QObject.connect(self.ui.startDownloadButton, QtCore.SIGNAL("clicked()"),
                        self.StartDownload )
                        
        # Connect the clicked signal of the Cancel to it's Slot - reject
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"),
                        self.reject )
                        
        QtCore.QObject.connect(self.ui.profileFilePath, QtCore.SIGNAL("editingFinished()"),
                        self.ControlStartDownloadBox )
        
    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtGui.QFileDialog.getOpenFileName(self, u'Select the file')
        # Show the selected file path in the field marked for showing directory path
        self.ui.profileFilePath.setText(directory)
        
        self.ControlStartDownloadBox()
        
    def StartDownload(self):
        # Do all the download related work here and then close
        self.accept()
    
    def ControlStartDownloadBox(self):
        if self.ui.profileFilePath.text().isEmpty():
            self.ui.startDownloadButton.setEnabled(False)
        else:
            self.ui.startDownloadButton.setEnabled(True)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtFetch()
    myapp.show()
    sys.exit(app.exec_())
