import sys
from PyQt4 import QtCore, QtGui

from Ui_AptOfflineQtMain import Ui_AptOfflineMain

from AptOfflineQtCreateProfile import AptOfflineQtCreateProfile
from AptOfflineQtFetch import AptOfflineQtFetch
from AptOfflineQtInstall import AptOfflineQtInstall

class AptOfflineQtMain(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineMain()
        self.ui.setupUi(self)
        
        # Configure the various actions
        self.ConfigureCreateProfile()
        self.ConfigureDownload()
        self.ConfigureInstall()
        self.ConfigureMenuExit()
        
        # Configure Hover over Buttons for Help
        self.CreateButtonHoverHelp()
        
    def ConfigureCreateProfile(self):
        QtCore.QObject.connect(self.ui.menuCreateProfile, QtCore.SIGNAL("triggered()"), self.CreateProfile)
        QtCore.QObject.connect(self.ui.createProfileButton,QtCore.SIGNAL("clicked()"), self.CreateProfile)
        # Create an object and do not show it
        self.createProfileDialog = AptOfflineQtCreateProfile()
        
    def ConfigureDownload(self):
        QtCore.QObject.connect(self.ui.menuDownload, QtCore.SIGNAL("triggered()"), self.DownloadPackagesUpgrades)
        QtCore.QObject.connect(self.ui.downloadButton, QtCore.SIGNAL("clicked()"), self.DownloadPackagesUpgrades)
        # Create an object for download dialog
        self.createDownloadDialog = AptOfflineQtFetch()
    
    def ConfigureInstall(self):
        QtCore.QObject.connect(self.ui.menuInstall, QtCore.SIGNAL("triggered()"), self.InstallPackagesUpgrades)
        QtCore.QObject.connect(self.ui.restoreButton, QtCore.SIGNAL("clicked()"), self.InstallPackagesUpgrades)
        # Create an object for Install dialog
        self.createInstallDialog = AptOfflineQtInstall()
        
    def ConfigureMenuExit(self):
        QtCore.QObject.connect(self.ui.menuExit, QtCore.SIGNAL("triggered()"), self.ExitApp)
        QtCore.QObject.connect(self.ui.exitButton, QtCore.SIGNAL("clicked()"), self.ExitApp)

    
    
    def CreateProfile(self):
        # Code for creating Modal Dialog for Create Profile
        self.createDownloadDialog.show()

    def DownloadPackagesUpgrades(self):
        # Code for creating Modal Dialog for Downloading Packages/Upgrades
        self.createDownloadDialog.show()

    def InstallPackagesUpgrades(self):
        # Code for creating Modal Dialog for Installing Packages/Upgrades
        self.createInstallDialog.show()

    def CreateButtonHoverHelp(self):
        pass

    def ExitApp(self):
        self.close()
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtMain()
    myapp.show()
    sys.exit(app.exec_())
