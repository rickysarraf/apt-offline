# -*- coding: utf-8 -*-
import sys,os
from PyQt5 import QtCore, QtGui, QtWidgets

from apt_offline_gui.Ui_AptOfflineQtCreateProfile import Ui_CreateProfile
from apt_offline_gui.UiDataStructs import SetterArgs
from apt_offline_gui import AptOfflineQtCommon as guicommon
import apt_offline_core.AptOfflineCoreLib


class AptOfflineQtCreateProfile(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_CreateProfile()
        self.ui.setupUi(self)

        # Connect the clicked signal of the Browse button to it's slot
        #QtCore.QObject.connect(self.ui.browseFilePathButton, QtCore.SIGNAL("clicked()"),
        #                self.popupDirectoryDialog )

        self.ui.browseFilePathButton.clicked.connect(self.popupDirectoryDialog)

        # Connect the clicked signal of the Save to it's Slot - accept
        #QtCore.QObject.connect(self.ui.createProfileButton, QtCore.SIGNAL("clicked()"),
        #                self.CreateProfile )

        self.ui.createProfileButton.clicked.connect(self.CreateProfile)

        # Connect the clicked signal of the Cancel to it's Slot - reject
        #QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"),
        #                self.reject )

        self.ui.cancelButton.clicked.connect(self.reject)

        # Disable or Enable the Package List field
        #QtCore.QObject.connect(self.ui.installPackagesCheckBox, QtCore.SIGNAL("toggled(bool)"),
        #                self.PackageListFieldStatus )

        self.ui.installPackagesCheckBox.toggled.connect(self.PackageListFieldStatus)

        #QtCore.QObject.connect(self.ui.installSrcPackagesCheckBox, QtCore.SIGNAL("toggled(bool)"),
        #                self.SrcPackageListFieldStatus )
        self.ui.installSrcPackagesCheckBox.toggled.connect(self.SrcPackageListFieldStatus)

        #QtCore.QObject.connect(self.ui.srcBuildDeps, QtCore.SIGNAL("toggled(bool)"),
        #                self.SrcPackageListFieldStatus )
        self.ui.srcBuildDeps.toggled.connect(self.SrcPackageListFieldStatus)

        #QtCore.QObject.connect(self.ui.targetReleaseCheckBox, QtCore.SIGNAL("toggled(bool)"),
        #                self.TargetReleaseFieldStatus )
        self.ui.targetReleaseCheckBox.toggled.connect(self.TargetReleaseFieldStatus)

        #QtCore.QObject.connect(self.ui.upgradePackagesCheckBox, QtCore.SIGNAL("toggled(bool)"),
        #                self.UpgradeCheckStatus )
        self.ui.upgradePackagesCheckBox.toggled.connect(self.UpgradeCheckStatus)

    def UpgradeCheckStatus(self):
        self.isFieldChecked = self.ui.upgradePackagesCheckBox.isChecked()

        self.ui.targetReleaseCheckBox.setEnabled(self.isFieldChecked)
        self.ui.generateChangelog.setEnabled(self.isFieldChecked)
        self.ui.upgradeTaskComboBox.setEnabled(self.isFieldChecked)

    def TargetReleaseFieldStatus(self):
        # If Install Packages Box is selected
        self.isFieldChecked = self.ui.targetReleaseCheckBox.isChecked()
        self.ui.targetReleaseTextInput.setEnabled(self.isFieldChecked)

    def SrcPackageListFieldStatus(self):
        # If Install Packages Box is selected
        self.isFieldChecked = self.ui.installSrcPackagesCheckBox.isChecked()
        self.ui.srcPackageList.setEnabled(self.isFieldChecked)
        self.ui.srcBuildDeps.setEnabled(self.isFieldChecked)

        self.ui.targetReleaseCheckBox.setEnabled(self.isFieldChecked)
        self.ui.upgradeTaskComboBox.setEnabled(self.isFieldChecked)


    def PackageListFieldStatus(self):
        # If Install Packages Box is selected
        self.isFieldChecked = self.ui.installPackagesCheckBox.isChecked()
        self.ui.packageList.setEnabled(self.isFieldChecked)

        self.ui.targetReleaseCheckBox.setEnabled(self.isFieldChecked)
        self.ui.generateChangelog.setEnabled(self.isFieldChecked)
        self.ui.upgradeTaskComboBox.setEnabled(self.isFieldChecked)

    def CreateProfile(self):
        # Is the Update requested
        self.updateChecked = self.ui.updateCheckBox.isChecked()
        # Is Upgrade requested
        self.upgradeChecked = self.ui.upgradePackagesCheckBox.isChecked()
        # Is Install Requested
        self.installChecked = self.ui.installPackagesCheckBox.isChecked()

        self.installSrcChecked = self.ui.installSrcPackagesCheckBox.isChecked()

        self.chlogChecked = self.ui.generateChangelog.isChecked()
        self.aptBackend = self.ui.aptBackendComboBox.currentText()
        self.upgradeType = self.ui.upgradeTaskComboBox.currentText()
        self.releaseBtnChecked = self.ui.targetReleaseCheckBox.isChecked()

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

        # If at least one is requested
        if self.updateChecked or self.upgradeChecked or self.installChecked or self.installSrcChecked:
            if self.installChecked:
                self.packageList = str(self.ui.packageList.text()).split(",")
            else:
                self.packageList = None

            if self.installSrcChecked:
                self.srcPackageList = str(self.ui.srcPackageList.text()).split(",")
                self.srcBuildDeps = self.ui.srcBuildDeps
            else:
                self.srcPackageList = None
                self.srcBuildDeps = False

            if self.releaseBtnChecked:
                self.release = str(self.ui.targetReleaseTextInput.text())
            else:
                self.release = None

            # setup i/o redirects before call
            sys.stdout = self
            sys.stderr = self

            args = SetterArgs(filename=self.filepath, update=self.updateChecked, upgrade=self.upgradeChecked, install_packages=self.packageList, \
                              install_src_packages=self.srcPackageList, src_build_dep=self.srcBuildDeps, changelog=self.chlogChecked, \
                              release=self.release, apt_backend=self.aptBackend, simulate=False)
            returnStatus = apt_offline_core.AptOfflineCoreLib.setter(args)

            if(returnStatus != False):  # right now it returns None, I think it doesn't return at all but sys.exits on failure
                # TODO ^ fixup this behaviour
                guicommon.updateInto(self.ui.consoleOutputHolder, guicommon.style("Completed.","green_fin"))
                self.ui.createProfileButton.setEnabled(False)
                self.ui.cancelButton.setText("Finish")
                self.ui.cancelButton.setIcon(QtGui.QIcon())
        else:
            pass


    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        signatureFilePath = os.path.join (os.path.expanduser("~"), "/Desktop/"+"apt-offline.sig")
        directory, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Select a filename to save the signature', signatureFilePath, "apt-offline Signatures (*.sig)")
        # Show the selected file path in the field marked for showing directory path
        self.ui.profileFilePath.setText(directory)

    def write(self, text):
        # redirects console output to our consoleOutputHolder
        text=text.strip()
        if (len(text)>2):
            guicommon.updateInto(self.ui.consoleOutputHolder,text)

    def flush(self):
        ''' nothing to do :D '''

    def resetUI(self):
        self.ui.updateCheckBox.setChecked(False)
        self.ui.upgradePackagesCheckBox.setChecked(False)
        self.ui.installPackagesCheckBox.setChecked(False)
        self.ui.cancelButton.setText("Close")
        self.ui.createProfileButton.setEnabled(True)
        self.ui.consoleOutputHolder.setText("")
        self.ui.profileFilePath.setText("")
        self.ui.packageList.setText("")
        self.ui.aptBackendComboBox.setCurrentIndex(0)
        self.ui.generateChangelog.setChecked(False)
        self.ui.srcBuildDeps.setChecked(False)
        self.ui.installSrcPackagesCheckBox.setChecked(False)
        self.ui.srcPackageList.setText("")
        self.ui.targetReleaseCheckBox.setChecked(False)
        self.ui.targetReleaseTextInput.setText("")


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtCreateProfile()
    myapp.show()
    sys.exit(app.exec_())
