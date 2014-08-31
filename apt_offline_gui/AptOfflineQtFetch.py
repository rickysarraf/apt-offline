# -*- coding: utf-8 -*-
import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox

from apt_offline_gui.Ui_AptOfflineQtFetch import Ui_AptOfflineQtFetch
from apt_offline_gui.UiDataStructs import GetterArgs
from apt_offline_gui import AptOfflineQtCommon as guicommon
import apt_offline_core.AptOfflineCoreLib

from apt_offline_gui.AptOfflineQtFetchOptions import AptOfflineQtFetchOptions

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
        apt_offline_core.AptOfflineCoreLib.fetcher(self.args)

    def setArgs (self,args):
        self.args = args

    def write(self, text):
        # redirects console output to our consoleOutputHolder
        # extract chinese whisper from text
        if apt_offline_core.AptOfflineCoreLib.guiTerminateSignal:
            # ^ so artificial, the threads still remain frozen in time I suppose
            return
            
        if ("MSG_START" in text):
            self.emit (QtCore.SIGNAL('status(QString)'), "Fetching missing meta data ...")
        elif ("MSG_END" in text):
            self.emit (QtCore.SIGNAL('status(QString)'), "Downloading packages ...")
        elif ("WARNING" in text):
            self.emit (QtCore.SIGNAL('output(QString)'), 
                                    guicommon.style(text,"red"))
        elif ("Downloading" in text):
            self.emit (QtCore.SIGNAL('output(QString)'), 
                                    guicommon.style(text,"orange"))
        elif ("done." in text):
            self.emit (QtCore.SIGNAL('output(QString)'), 
                                    guicommon.style(text,"green"))
        elif ("[" in text and "]" in text):
            try:
                # no more splits, we know the exact byte count now
                progress = str(apt_offline_core.AptOfflineCoreLib.totalSize[1])
                total = str(apt_offline_core.AptOfflineCoreLib.totalSize[0])
                self.emit (QtCore.SIGNAL('progress(QString,QString)'), progress,total)
            except:
                ''' nothing to do '''
        else:
            self.emit (QtCore.SIGNAL('output(QString)'), text.strip())

    def flush(self):
        ''' nothing to do :D '''

    def quit(self):
        self.emit (QtCore.SIGNAL('finished()'))


class AptOfflineQtFetch(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineQtFetch()
        self.ui.setupUi(self)
        self.advancedOptionsDialog = AptOfflineQtFetchOptions()
        
        # Connect the clicked signal of the Signature File Browse button to it's slot
        QtCore.QObject.connect(self.ui.browseFilePathButton, QtCore.SIGNAL("clicked()"),
                        self.popupDirectoryDialog )
        
        # Connect the clicked signal of the Zip File Browse button to it's slot
        QtCore.QObject.connect(self.ui.browseZipFileButton, QtCore.SIGNAL("clicked()"),
                        self.popupZipFileDialog )
                                                
        # Connect the clicked signal of the Save to it's Slot - accept
        QtCore.QObject.connect(self.ui.startDownloadButton, QtCore.SIGNAL("clicked()"),
                        self.StartDownload )
                        
        # Connect the clicked signal of the Cancel to it's Slot - reject
        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"),
                        self.handleCancel )
                        
        QtCore.QObject.connect(self.ui.profileFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.controlStartDownloadBox )

        QtCore.QObject.connect(self.ui.profileFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.controlStartDownloadBox )
        QtCore.QObject.connect(self.ui.zipFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.controlStartDownloadBox )
        QtCore.QObject.connect(self.ui.zipFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.controlStartDownloadBox )
        
        QtCore.QObject.connect(self.ui.advancedOptionsButton, QtCore.SIGNAL("clicked()"),
                        self.showAdvancedOptions )
        
        
        
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
        

        #INFO: inform CLI that it's a gui app
        apt_offline_core.AptOfflineCoreLib.guiBool = True
        # Reduce extra line gaps in CLI o/p
        apt_offline_core.AptOfflineCoreLib.LINE_OVERWRITE_SMALL=""
        apt_offline_core.AptOfflineCoreLib.LINE_OVERWRITE_MID=""
        apt_offline_core.AptOfflineCoreLib.LINE_OVERWRITE_FULL=""

    def showAdvancedOptions(self):
            self.advancedOptionsDialog.show()
    
    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtGui.QFileDialog.getOpenFileName(self, u'Select the signature file')
        # Show the selected file path in the field marked for showing directory path
        self.ui.profileFilePath.setText(directory)
        
        self.controlStartDownloadBox()
    
    def popupZipFileDialog(self):
        
        if self.ui.saveDatacheckBox.isChecked() is True:
                filename = QtGui.QFileDialog.getExistingDirectory(self, u'Select the folder to save downlaods to')
        else:
                # Popup a Zip File selection box
                filename = QtGui.QFileDialog.getSaveFileName(self, u'Select the zip file to save downloads')
        
        # Show the selected file path in the field marked for showing directory path
        self.ui.zipFilePath.setText(filename)
        
        self.controlStartDownloadBox()
        
    def StartDownload(self):
        # Do all the download related work here and then close

        # Clear the consoleOutputHolder
        self.ui.rawLogHolder.setText("")
        
        self.filepath = str(self.ui.profileFilePath.text())

        if os.path.isfile(self.filepath) == False:
            if (len(self.filepath) == 0):
                self.ui.rawLogHolder.setText ( \
                    guicommon.style("Please select a signature file!",'red'))
            else:
                self.ui.rawLogHolder.setText ( \
                    guicommon.style("%s does not exist." % self.filepath,'red'))
            return
        
        self.zipfilepath = str(self.ui.zipFilePath.text())
        
        # First we need to determine if the input is a file path or a directory path
        if self.ui.saveDatacheckBox.isChecked() is not True: 
                #Input is a file path

                # if file already exists
                if os.path.exists(self.zipfilepath):
                        ret = QMessageBox.warning(self, "Replace archive file?", "The file %s already exists.\n" 
                                                  "Do you want to overwrite it?" % self.zipfilepath,
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                        if ret == QMessageBox.Yes:
                                # delete the file
                                try:
                                        #TODO: If "/" is the path, then os.unlink quietly fails crashing the GUI
                                        os.unlink(self.zipfilepath)
                                except:
                                        guicommon.updateInto (self.ui.rawLogHolder, 
                                                              guicommon.style("Could'nt write to %s!" % self.zipfilepath,'red'))
                        else:
                                return
                else:
                        if not os.access(os.path.dirname(self.zipfilepath), os.W_OK):
                                guicommon.updateInto (self.ui.rawLogHolder,
                                                      guicommon.style("%s does not have write access." % self.zipfilepath,'red'))
                                return
                targetFilePath = self.zipfilepath
                targetDirPath = None
                    
        else:
                if os.path.exists(self.zipfilepath):
                        if os.access(self.zipfilepath, os.W_OK) == False:
                                guicommon.updateInto (self.ui.rawLogHolder,
                                                      guicommon.style("%s does not have write access." % self.zipfilepath,'red'))
                        return
                else:
                        ret = QMessageBox.warning(self, "No such directory", "No such directory %s\n"
                                                  "Do you want to create it?" % self.zipfilepath,
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                        if ret == QMessageBox.Yes:
                                # delete the file
                                try:
                                        os.mkdir(self.zipfilepath)
                                except:
                                        guicommon.updateInto (self.ui.rawLogHolder, 
                                                              guicommon.style("Couldn't create directory %s!" % self.zipfilepath,'red'))
                                        return
                        else:
                                return
                targetFilePath = None
                targetDirPath = self.zipfilepath

        
        args = GetterArgs(filename=self.filepath, bundle_file=targetFilePath, progress_bar=self.ui.statusProgressBar, 
                        progress_label=self.ui.progressStatusDescription, proxy_host=self.advancedOptionsDialog.proxy_host,
                        proxy_port=self.advancedOptionsDialog.proxy_port, num_of_threads=self.advancedOptionsDialog.num_of_threads,
                        socket_timeout=self.advancedOptionsDialog.socket_timeout, cache_dir=self.advancedOptionsDialog.cache_dir,
                        download_dir=targetDirPath, disable_md5check=self.advancedOptionsDialog.disable_md5check,
                        deb_bugs=self.advancedOptionsDialog.deb_bugs)
        
        #returnStatus = apt_offline_core.AptOfflineCoreLib.fetcher(args)
        # TODO: deal with return status laters
        
        self.ui.cancelButton.setText("Cancel")
        self.disableAction()
        self.disableAtDownload()
        self.worker.setArgs (args)
        self.worker.start()
        
        #if (returnStatus):
        ''' TODO: do something with self.zipfilepath '''
            
        # TODO to be implemented later
        # self.accept()

    def updateLog(self,text):
        if not ('[' in text and ']' in text):
            if ('Downloaded data ' in text):
                guicommon.updateInto (self.ui.rawLogHolder,
                                    guicommon.style(text,'green_fin'))
                self.ui.progressStatusDescription.setText('Finished.')
            else:
                guicommon.updateInto (self.ui.rawLogHolder,text)

    def updateStatus(self,text):
        self.ui.progressStatusDescription.setText(text)

    def updateProgress(self,progress,total):
        try:
            # try parsing numbers and updating progressBar
            percent = (float(progress)/float(total))*100
            self.ui.statusProgressBar.setValue (percent)
        except:
            ''' nothing to do '''

    def controlStartDownloadBox(self):
        if self.ui.profileFilePath.text().isEmpty():
            self.disableAction()
        if self.ui.zipFilePath.text().isEmpty():
            self.disableAction()
        else:
            self.enableAction()

    def handleCancel(self):
        if self.ui.cancelButton.text() == "Cancel":
            if self.worker.isRunning():
                # Download is still in progress
                ret = QMessageBox.warning(self, "Cancel current downloads?",
                    "A download is already in progress.\nDo you want to cancel it?",
                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if ret == QMessageBox.Yes:
                    # we can't just stop threads, we need to pass message
                    apt_offline_core.AptOfflineCoreLib.guiTerminateSignal=True
                    self.updateStatus(guicommon.style("Download aborted","red"))
                    self.enableAtStop()
                    self.ui.cancelButton.setText("Close")
            else:
                self.reject()
        else:
            self.reject()

    def resetUI(self):
        apt_offline_core.AptOfflineCoreLib.guiTerminateSignal=False
        apt_offline_core.AptOfflineCoreLib.guiMetaCompleted=False
        apt_offline_core.AptOfflineCoreLib.errlist = []
        apt_offline_core.AptOfflineCoreLib.totalSize = [0,0]
        self.ui.profileFilePath.setText("")
        self.ui.zipFilePath.setText("")
        self.ui.rawLogHolder.setText("")
        self.ui.statusProgressBar.setValue(0)
        self.updateStatus("Ready")
        self.enableAction()
        self.enableAtStop()

    def disableAction(self):
        self.ui.startDownloadButton.setEnabled(False)
    
    def disableAtDownload(self):
        self.ui.advancedOptionsButton.setEnabled(False)
        self.ui.browseZipFileButton.setEnabled(False)
        self.ui.browseFilePathButton.setEnabled(False)
        self.ui.zipFilePath.setEnabled(False)
        self.ui.profileFilePath.setEnabled(False)
        self.ui.saveDatacheckBox.setEnabled(False)
            
    def enableAction(self):
        self.ui.startDownloadButton.setEnabled(True)

    def enableAtStop(self):
        self.ui.advancedOptionsButton.setEnabled(True)
        self.ui.browseZipFileButton.setEnabled(True)
        self.ui.browseFilePathButton.setEnabled(True)
        self.ui.zipFilePath.setEnabled(True)
        self.ui.profileFilePath.setEnabled(True)
        self.ui.saveDatacheckBox.setEnabled(True)

    def finishedWork(self):
        ''' do nothing '''
        self.ui.cancelButton.setText("Close")

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtFetch()
    myapp.show()
    sys.exit(app.exec_())


