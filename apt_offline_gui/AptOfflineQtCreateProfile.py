import sys
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtCreateProfile import Ui_CreateProfile


class AptOfflineQtCreateProfile(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_CreateProfile()
        self.ui.setupUi(self)
        
        # Connect the clicked signal of the Browse button to it's slot
        QtCore.QObject.connect(self.ui.browseFilePathButton, QtCore.SIGNAL("clicked()"),
                        self.popupDirectoryDialog )
                        
        # Connect the clicked signal of the Save to it's Slot - accept
        QtCore.QObject.connect(self.ui.createProfileButton, QtCore.SIGNAL("clicked()"),
                        self.CreateProfile )
                        
        # Connect the clicked signal of the Cancel to it's Slot - reject
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"),
                        self.reject )
        
        # Disable or Enable the Package List field
        QtCore.QObject.connect(self.ui.installPackagesRadioBox, QtCore.SIGNAL("toggled(bool)"),
                        self.PackageListFieldStatus )
        
    def PackageListFieldStatus(self):
        # If Install Packages Box is selected
        self.isFieldChecked = self.ui.installPackagesRadioBox.isChecked()
        self.ui.packageList.setEnabled(self.isFieldChecked)
    
    def CreateProfile(self):
        # Create the profile here and then exit
        self.accept()
    
    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtGui.QFileDialog.getExistingDirectory(self, u'Open Directory')
        # Show the selected file path in the field marked for showing directory path
        self.ui.profileFilePath.setText(directory)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtCreateProfile()
    myapp.show()
    sys.exit(app.exec_())
