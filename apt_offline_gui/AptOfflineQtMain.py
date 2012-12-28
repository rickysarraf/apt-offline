import sys, os
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtMain import Ui_AptOfflineMain

from apt_offline_gui.AptOfflineQtCreateProfile import AptOfflineQtCreateProfile
from apt_offline_gui.AptOfflineQtFetch import AptOfflineQtFetch
from apt_offline_gui.AptOfflineQtInstall import AptOfflineQtInstall
from apt_offline_gui.AptOfflineQtAbout import AptOfflineQtAbout

class AptOfflineQtMain(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineMain()
        self.ui.setupUi(self)
        
        # Configure the various actions
        self.ConfigureCreateProfile()
        self.ConfigureDownload()
        self.ConfigureInstall()
        self.ConfigureAbout()
        self.ConfigureMenuExit()
        
        # Configure Hover over Buttons for Help
        self.CreateButtonHoverHelp()
        
    def ConfigureCreateProfile(self):
        QtCore.QObject.connect(self.ui.menuCreateProfile, QtCore.SIGNAL("triggered()"), self.CreateProfile)
        QtCore.QObject.connect(self.ui.createProfileButton,QtCore.SIGNAL("clicked()"), self.CreateProfile)
        # Create an object and do not show it
        self.createProfileDialog = AptOfflineQtCreateProfile()
        # setup hover hack
        self.ui.createProfileButton.installEventFilter(self)
        
    def ConfigureDownload(self):
        QtCore.QObject.connect(self.ui.menuDownload, QtCore.SIGNAL("triggered()"), self.DownloadPackagesUpgrades)
        QtCore.QObject.connect(self.ui.downloadButton, QtCore.SIGNAL("clicked()"), self.DownloadPackagesUpgrades)
        # Create an object for download dialog
        self.createDownloadDialog = AptOfflineQtFetch()
        # setup hover hack
        self.ui.downloadButton.installEventFilter(self)
    
    def ConfigureInstall(self):
        QtCore.QObject.connect(self.ui.menuInstall, QtCore.SIGNAL("triggered()"), self.InstallPackagesUpgrades)
        QtCore.QObject.connect(self.ui.restoreButton, QtCore.SIGNAL("clicked()"), self.InstallPackagesUpgrades)
        # Create an object for Install dialog
        self.createInstallDialog = AptOfflineQtInstall()
        # setup hover hack
        self.ui.restoreButton.installEventFilter(self)

    def ConfigureAbout(self):
        QtCore.QObject.connect(self.ui.menuAbout, QtCore.SIGNAL("triggered()"), self.ShowAbout)
        # Create an object for About Dialog
        self.createAboutDialog = AptOfflineQtAbout()
        
    def ConfigureMenuExit(self):
        QtCore.QObject.connect(self.ui.menuExit, QtCore.SIGNAL("triggered()"), self.ExitApp)
        QtCore.QObject.connect(self.ui.exitButton, QtCore.SIGNAL("clicked()"), self.ExitApp)

    def eventFilter(self,target,event):
        # hover hack for 3 buttons
        if event.type() == QtCore.QEvent.HoverEnter:
            if target.objectName() == 'createProfileButton':
                self.ui.descriptionField.setText("Click here to generate a signature of this machine.")
            if target.objectName() == 'downloadButton':
                self.ui.descriptionField.setText("Once you are on a internet connected machine, use this to download packages as per your signature file.")
            if target.objectName() == 'restoreButton':
                self.ui.descriptionField.setText("Once you've downloaded all the packages, click here to install them on the offline machine.")
                
        if event.type() == QtCore.QEvent.HoverLeave:
            self.ui.descriptionField.setText("Hover your mouse over the buttons to get the description.")
        return False
        
    
    def CreateProfile(self):
        if os.geteuid() != 0:
                QtGui.QMessageBox.critical(self, "Error", "You need to run with root priviliges")
                return
        # Code for creating Modal Dialog for Create Profile
        self.createProfileDialog.resetUI()
        self.createProfileDialog.show()

    def DownloadPackagesUpgrades(self):
        # Code for creating Modal Dialog for Downloading Packages/Upgrades
        self.createDownloadDialog.resetUI()
        self.createDownloadDialog.show()

    def InstallPackagesUpgrades(self):
        #if os.geteuid() != 0:
        #        QtGui.QMessageBox.critical(self, "Error", "You need to run with root priviliges")
        #        return
        # Code for creating Modal Dialog for Installing Packages/Upgrades
        self.createInstallDialog.show()
    
    def ShowAbout(self):
        # Code for showing Model Dialog for About Application
        self.createAboutDialog.show()

    def CreateButtonHoverHelp(self):
        pass

    def ExitApp(self):
        self.close()

