# -*- coding: utf-8 -*-
import sys,os
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtCreateProfile import Ui_CreateProfile
from apt_offline_gui.UiDataStructs import SetterArgs
from apt_offline_gui import AptOfflineQtCommon as guicommon
import apt_offline_core.AptOfflineCoreLib


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
        # Is the Update requested
        self.updateChecked = self.ui.updateCheckBox.isChecked()
        # Is Upgrade requested
        self.upgradeChecked = self.ui.upgradePackagesRadioBox.isChecked()
        # Is Install Requested
        self.installChecked = self.ui.installPackagesRadioBox.isChecked()

        # Clear the consoleOutputHolder
        self.ui.consoleOutputHolder.setText("")
        
        self.filepath = str(self.ui.profileFilePath.text())
        
        if os.path.exists(os.path.dirname(self.filepath)) == False:
            if (len(self.filepath) == 0):
                self.ui.consoleOutputHolder.setText ( \
                    guicommon.style("Please select a file to store the signature!",'red'))
            else:
                self.ui.consoleOutputHolder.setText ( \
                    guicommon.style("Could not access  %s" % self.filepath,'red'))
            return
        
        # If atleast one is requested
        if self.updateChecked or self.upgradeChecked or self.installChecked:
            if self.installChecked:
                self.packageList = str(self.ui.packageList.text()).split(",")
            else:
                self.packageList = None

            # setup i/o redirects before call
            sys.stdout = self
            sys.stderr = self
            
            args = SetterArgs(filename=self.filepath, update=self.updateChecked, upgrade=self.upgradeChecked, install_packages=self.packageList, simulate=False)
            returnStatus = apt_offline_core.AptOfflineCoreLib.setter(args)
            
            if(returnStatus):
                self.ui.createProfileButton.setEnabled(False)
                self.ui.cancelButton.setText("Finish")
                self.ui.cancelButton.setIcon(QtGui.QIcon())
        else:
            pass
        
    
    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        signatureFilePath = os.path.join (os.path.expanduser("~"), "/Desktop/"+"apt-offline.sig")
        directory = QtGui.QFileDialog.getSaveFileName(self, u'Select a filename to save the signature', signatureFilePath, "apt-offline Signatures (*.sig)")
        # Show the selected file path in the field marked for showing directory path
        self.ui.profileFilePath.setText(directory)

    def write(self, text):
        # redirects console output to our consoleOutputHolder
        guicommon.updateInto(self.ui.consoleOutputHolder,text)

    def flush(self):
        ''' nothing to do :D '''


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtCreateProfile()
    myapp.show()
    sys.exit(app.exec_())
