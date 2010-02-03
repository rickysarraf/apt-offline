import sys
from PyQt4 import QtCore, QtGui

from Ui_AptOfflineQtMain import Ui_MainWindow


class AptOfflineQtMain(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
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
        
    def ConfigureDownload(self):
        QtCore.QObject.connect(self.ui.menuDownload, QtCore.SIGNAL("triggered()"), self.DownloadPackagesUpgrades)
        QtCore.QObject.connect(self.ui.downloadButton, QtCore.SIGNAL("clicked()"), self.DownloadPackagesUpgrades)
    
    def ConfigureInstall(self):
        QtCore.QObject.connect(self.ui.menuInstall, QtCore.SIGNAL("triggered()"), self.InstallPackagesUpgrades)
        QtCore.QObject.connect(self.ui.restoreButton, QtCore.SIGNAL("clicked()"), self.InstallPackagesUpgrades)
        
    def ConfigureMenuExit(self):
        QtCore.QObject.connect(self.ui.menuExit, QtCore.SIGNAL("triggered()"), self.ExitApp)
        QtCore.QObject.connect(self.ui.exitButton, QtCore.SIGNAL("clicked()"), self.ExitApp)

    
    
    def CreateProfile(self):
        # Code for creating Modal Dialog for Create Profile
        print "Create New Profile"

    def DownloadPackagesUpgrades(self):
        # Code for creating Modal Dialog for Downloading Packages/Upgrades
        print "Download packages or upgrades"

    def InstallPackagesUpgrades(self):
        # Code for creating Modal Dialog for Installing Packages/Upgrades
        print "Installing packages or upgrades"

    def CreateButtonHoverHelp(self):
        pass

    def ExitApp(self):
        self.close()
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtMain()
    myapp.show()
    sys.exit(app.exec_())
