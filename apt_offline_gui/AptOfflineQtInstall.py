# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, QtGui, QtWidgets

from apt_offline_gui.Ui_AptOfflineQtInstall import Ui_AptOfflineQtInstall
from apt_offline_gui.UiDataStructs import InstallerArgs
from apt_offline_gui import AptOfflineQtCommon as guicommon
import apt_offline_core.AptOfflineCoreLib

from apt_offline_gui.AptOfflineQtInstallBugList import AptOfflineQtInstallBugList
from apt_offline_gui.AptOfflineQtInstallChangelog import AptOfflineQtInstallChangelog

class Worker(QtCore.QThread):

    output = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(str, str)
    status = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    terminated = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self):
        # setup i/o redirects before call
        sys.stdout = self
        sys.stderr = self
        apt_offline_core.AptOfflineCoreLib.installer(self.args)

    def setArgs (self,args):
        self.args = args

    def write(self, text):
        # redirects console output to our consoleOutputHolder
        # extract details from text
        if ('.deb' in text and 'synced' in text):
            try:
                text = guicommon.style("Package : ",'orange') + guicommon.style(text.split("/")[-1],'green')
            except:
                pass
            self.output.emit(text)
        elif ('apt/lists' in text):
            try:
                # this part is always done on a Linux system so we can hardcode / for a while
                text = guicommon.style("Update : ",'orange') + guicommon.style(text.split("/")[-1],'green')
            except:
                # let the text be original otherwise
                pass
            self.output.emit(text)
        elif ('[' in text and ']' in text):
            try:
                progress = str(apt_offline_core.AptOfflineCoreLib.totalSize[0])
                total = str(apt_offline_core.AptOfflineCoreLib.totalSize[1])
                self.progress.emit("%s%s" % (progress, total))
            except:
                ''' nothing to do '''
        else:
            self.output.emit(text)

    def flush(self):
        ''' nothing to do :D '''

    def quit(self):
        self.finished.emit()


class AptOfflineQtInstall(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineQtInstall()
        self.ui.setupUi(self)

        # Connect the clicked signal of the Browse button to it's slot
        self.ui.browseFilePathButton.clicked.connect(self.popupDirectoryDialog)

        # Connect the clicked signal of the Save to it's Slot - accept
        self.ui.startInstallButton.clicked.connect(self.StartInstall)

        # Connect the clicked signal of the Cancel to it's Slot - reject
        self.ui.cancelButton.clicked.connect(self.reject)

        self.ui.bugReportsButton.clicked.connect(self.showBugReports)
        self.ui.changelogButton.clicked.connect(self.showChangelog)
        self.ui.zipFilePath.editingFinished.connect(self.ControlStartInstallBox)
        self.ui.zipFilePath.textChanged.connect(self.ControlStartInstallBox)

        self.worker = Worker(parent=self)
        self.worker.output.connect(self.updateLog)
        self.worker.progress.connect(self.updateProgress)
        self.worker.status.connect(self.updateStatus)
        self.worker.finished.connect(self.finishedWork)
        self.worker.terminated.connect(self.finishedWork)

    def StartInstall(self):
        # gui validation
        # Clear the consoleOutputHolder
        self.ui.rawLogHolder.setText("")
        self.filepath = str(self.ui.zipFilePath.text())

        # parse args
        args = InstallerArgs(filename=self.filepath, progress_bar=self.ui.statusProgressBar, progress_label=self.ui.progressStatusDescription )

        self.disableActions()
        self.ui.progressStatusDescription.setText("Syncing updates")
        self.worker.setArgs (args)
        self.worker.start()

    def showBugReports(self):
        self.filepath = str(self.ui.zipFilePath.text())
        self.bugReportsDialog = AptOfflineQtInstallBugList(self.filepath)
        self.bugReportsDialog.filepath= self.filepath
        self.bugReportsDialog.show()

    def showChangelog(self):
        self.filepath = str(self.ui.zipFilePath.text())
        self.changelogDialog = AptOfflineQtInstallChangelog(self.filepath)
        self.changelogDialog.filepath = self.filepath
        self.changelogDialog.show()

    def popupDirectoryDialog(self):

        # Popup a Directory selection box
        if self.ui.browseFileFoldercheckBox.isChecked() is True:
                directory  = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the folder')
        else:
                directory = QtWidgets.QFileDialog.getOpenFileName(self, 'Select the Zip File')

        # Show the selected file path in the field marked for showing directory path
        self.ui.zipFilePath.setText(directory)
        self.ui.zipFilePath.setFocus()

    def ControlStartInstallBox(self):
        if os.path.isdir(self.ui.zipFilePath.text()) or os.path.isfile(self.ui.zipFilePath.text() ):
            self.ui.startInstallButton.setEnabled(True)
            self.ui.bugReportsButton.setEnabled(True)
            self.ui.changelogButton.setEnabled(True)
        else:
            self.ui.startInstallButton.setEnabled(False)
            self.ui.bugReportsButton.setEnabled(False)
            self.ui.changelogButton.setEnabled(False)

    def updateLog(self,text):
        guicommon.updateInto (self.ui.rawLogHolder,text)

    def updateStatus(self,text):
        # status handler
        self.ui.progressStatusDescription.setText(text)

    def updateProgress(self,progress,total):
        try:
            # try parsing numbers and updating progressBar
            percent = (float(progress)/float(total))*100
            self.ui.statusProgressBar.setValue (percent)
        except:
            ''' nothing to do '''

    def finishedWork(self):
        self.enableActions()
        guicommon.updateInto (self.ui.rawLogHolder,
            guicommon.style("Finished syncing updates/packages","green_fin"))
        self.ui.progressStatusDescription.setText("Finished Syncing")
        self.ui.cancelButton.setText("Close")

    def disableActions(self):
        self.ui.browseFileFoldercheckBox.setEnabled(False)
        self.ui.cancelButton.setEnabled(False)
        self.ui.startInstallButton.setEnabled(False)
        self.ui.bugReportsButton.setEnabled(False)
        self.ui.browseFilePathButton.setEnabled(False)
        self.ui.zipFilePath.setEnabled(False)
        self.ui.changelogButton.setEnabled(False)

    def enableActions(self):
        self.ui.browseFileFoldercheckBox.setEnabled(True)
        self.ui.cancelButton.setEnabled(True)
        self.ui.startInstallButton.setEnabled(True)
        self.ui.bugReportsButton.setEnabled(True)
        self.ui.browseFilePathButton.setEnabled(True)
        self.ui.zipFilePath.setEnabled(True)
        self.ui.changelogButton.setEnabled(True)


if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        myapp = AptOfflineQtInstall()
        myapp.show()
        sys.exit(app.exec_())
