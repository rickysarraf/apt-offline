# -*- coding: utf-8 -*-
import os, sys
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtInstall import Ui_AptOfflineQtInstall
from apt_offline_gui.UiDataStructs import InstallerArgs
from apt_offline_gui import AptOfflineQtCommon as guicommon
import apt_offline_core.AptOfflineCoreLib

from apt_offline_gui.AptOfflineQtInstallBugList import AptOfflineQtInstallBugList
from apt_offline_gui.AptOfflineQtInstallChangelog import AptOfflineQtInstallChangelog

class Worker(QtCore.QThread):
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
        # extract chinese whisper from text
        if ('.deb' in text and 'synced' in text):
            try:
                text = guicommon.style("Package : ",'orange') + guicommon.style(text.split("/")[-1],'green')
            except:
                pass
            self.emit (QtCore.SIGNAL('output(QString)'), text)
        elif ('apt/lists' in text):
            try:
                # this part is always done on a linux system so we can hardcode / for a while
                text = guicommon.style("Update : ",'orange') + guicommon.style(text.split("/")[-1],'green')
            except:
                # let the text be original otherwise
                pass
            self.emit (QtCore.SIGNAL('output(QString)'), text)
        elif ('[' in text and ']' in text):
            try:
                progress = str(apt_offline_core.AptOfflineCoreLib.totalSize[0])
                total = str(apt_offline_core.AptOfflineCoreLib.totalSize[1])
                self.emit (QtCore.SIGNAL('progress(QString,QString)'), progress,total)
            except:
                ''' nothing to do '''
        else:
            self.emit (QtCore.SIGNAL('output(QString)'), guicommon.style(text,'red'))
                            
    def flush(self):
        ''' nothing to do :D '''
        
    def quit(self):
        self.emit (QtCore.SIGNAL('finished()'))
        
        
class AptOfflineQtInstall(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineQtInstall()
        self.ui.setupUi(self)
        
        # Connect the clicked signal of the Browse button to it's slot
        QtCore.QObject.connect(self.ui.browseFilePathButton, QtCore.SIGNAL("clicked()"),
                        self.popupDirectoryDialog )
                        
        # Connect the clicked signal of the Save to it's Slot - accept
        QtCore.QObject.connect(self.ui.startInstallButton, QtCore.SIGNAL("clicked()"),
                        self.StartInstall )
                        
        # Connect the clicked signal of the Cancel to it's Slot - reject
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"),
                        self.reject )
        
        QtCore.QObject.connect(self.ui.bugReportsButton, QtCore.SIGNAL("clicked()"),
                        self.showBugReports )
        
        QtCore.QObject.connect(self.ui.changelogButton, QtCore.SIGNAL("clicked()"),
                        self.showChangelog )
        
        QtCore.QObject.connect(self.ui.zipFilePath, QtCore.SIGNAL("editingFinished()"),
                        self.ControlStartInstallBox )

        QtCore.QObject.connect(self.ui.zipFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.ControlStartInstallBox )
        
        self.worker = Worker(parent=self)
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("output(QString)"),
                        self.updateLog )
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("progress(QString,QString)"),
                        self.updateProgress )
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("status(QString)"),
                        self.updateStatus )
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("finished()"),
                        self.finishedWork )
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("terminated()"),
                        self.finishedWork )
        
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
                directory  = QtGui.QFileDialog.getExistingDirectory(self, 'Select the folder')
        else:
                directory = QtGui.QFileDialog.getOpenFileName(self, 'Select the Zip File')
        
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
        
    def disableActions(self):
        self.ui.cancelButton.setEnabled(False)
        self.ui.startInstallButton.setEnabled(False)
        self.ui.bugReportsButton.setEnabled(False)
        self.ui.browseFilePathButton.setEnabled(False)
        self.ui.zipFilePath.setEnabled(False)
        self.ui.changelogButton.setEnabled(False)

    def enableActions(self):
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
