# -*- coding: utf-8 -*-
import os,sys, thread
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtInstall import Ui_AptOfflineQtInstall
from apt_offline_gui.UiDataStructs import InstallerArgs
from apt_offline_gui import AptOfflineQtCommon as guicommon
import apt_offline_core.AptOfflineCoreLib

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
        self.emit (QtCore.SIGNAL('output(QString)'), text)
        return
        '''
        # TODO: if backend sends out any progress, error or success messages,
        #       rewrite UI handlers here
        
        if ("MSG_START" in text):
            self.emit (QtCore.SIGNAL('status(QString)'), "Fetching missing meta data ...")
            return
        if ("MSG_END" in text):
            self.emit (QtCore.SIGNAL('status(QString)'), "Downloading packages ...")
            return
            
        if ("[" in text and "]" in text):
            try:
                # no more splits, we know the exact byte count now
                progress = str(apt_offline_core.AptOfflineCoreLib.totalSize[1])
                total = str(apt_offline_core.AptOfflineCoreLib.totalSize[0])
                self.emit (QtCore.SIGNAL('progress(QString,QString)'), progress,total)
                return
            except:
                pass
            
        self.emit (QtCore.SIGNAL('output(QString)'), text)
        '''

    def flush(self):
        ''' nothing to do :D '''
        
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
        
    def StartInstall(self):
        # gui validation
        # Clear the consoleOutputHolder
        self.ui.rawLogHolder.setText("")

        self.filepath = str(self.ui.zipFilePath.text())

        if os.path.isfile(self.filepath) == False:
            if (len(self.filepath) == 0):
                self.ui.rawLogHolder.setText ( \
                    guicommon.style("Please select a zip file!",'red'))
            else:
                self.ui.rawLogHolder.setText ( \
                    guicommon.style("%s does not exist." % self.filepath,'red'))
            return

        # parse args
        args = InstallerArgs(filename=self.filepath, progress_bar=self.ui.statusProgressBar, progress_label=self.ui.progressStatusDescription )

        self.worker.setArgs (args)
        self.worker.start()
        ''' old discarded imcompatible threading '''
        # setup i/o redirects before call
        #sys.stdout = self
        #sys.stderr = self
        # returnStatus = apt_offline_core.AptOfflineCoreLib.installer(args)
        # TODO: deal with return status laters
        #thread.start_new_thread (apt_offline_core.AptOfflineCoreLib.installer, (args,))
        # TODO to be implemented later
        # self.accept()

    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtGui.QFileDialog.getOpenFileName(self, u'Select the Zip File')
        # Show the selected file path in the field marked for showing directory path
        self.ui.zipFilePath.setText(directory)
        self.ui.zipFilePath.setFocus()
    
    def ControlStartInstallBox(self):
        if self.ui.zipFilePath.text().isEmpty():
            self.ui.startInstallButton.setEnabled(False)
        else:
            self.ui.startInstallButton.setEnabled(True)
            
    def updateLog(self,text):
        guicommon.updateInto (self.ui.rawLogHolder,text)

    def updateStatus(self,text):
        # status handler
        self.ui.progressStatusDescription.setText(text)

    def updateProgress(self,progress,total):
        # NOTE: inactive
        # TODO: implement progress here
        return


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtInstall()
    myapp.show()
    sys.exit(app.exec_())
