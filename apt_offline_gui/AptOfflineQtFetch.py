# -*- coding: utf-8 -*-
import os, sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMessageBox

from apt_offline_gui.Ui_AptOfflineQtFetch import Ui_AptOfflineQtFetch
from apt_offline_gui.UiDataStructs import GetterArgs
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
        
        apt_offline_core.AptOfflineCoreLib.fetcher(self.args)

    def setArgs (self,args):
        self.args = args

    def write(self, text):
        # redirects console output to our consoleOutputHolder
        # extract chinese whisper from text
        if (" / " in text):
            try:
                # no more splits, we know the exact byte count now
                progress = str(apt_offline_core.AptOfflineCoreLib.totalSize[1])
                total = str(apt_offline_core.AptOfflineCoreLib.totalSize[0])
                self.emit (QtCore.SIGNAL('progress(QString,QString)'), progress,total)
                return
            except:
                ''' nothing to do '''
        
        if " _META_ " in text:
            progress = str(apt_offline_core.AptOfflineCoreLib.totalUrls[1])
            total = str(apt_offline_core.AptOfflineCoreLib.totalUrls[0])
            self.emit (QtCore.SIGNAL('progress(QString,QString)'), progress,total)
            return
            
        if "META_START" in text:
            self.emit (QtCore.SIGNAL('status(QString)'), 'Fetching metadata...')
            return
        if "META_END" in text:
            self.emit (QtCore.SIGNAL('status(QString)'), 'Downloading packages...')
            return
            
        self.emit (QtCore.SIGNAL('output(QString)'), text)

    def flush(self):
        ''' nothing to do :D '''


class AptOfflineQtFetch(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_AptOfflineQtFetch()
        self.ui.setupUi(self)
        
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
                        self.reject )
                        
        QtCore.QObject.connect(self.ui.profileFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.ControlStartDownloadBox )

        QtCore.QObject.connect(self.ui.profileFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.ControlStartDownloadBox )
                        
        QtCore.QObject.connect(self.ui.zipFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.ControlStartDownloadBox )
        
        QtCore.QObject.connect(self.ui.zipFilePath, QtCore.SIGNAL("textChanged(QString)"),
                        self.ControlStartDownloadBox )
                        
        self.worker = Worker(parent=self)
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("output(QString)"),
                        self.updateLog )
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("progress(QString,QString)"),
                        self.updateProgress )
        QtCore.QObject.connect(self.worker, QtCore.SIGNAL("status(QString)"),
                        self.updateStatus )
                        
        #INFO: inform CLI that it's a gui app
        apt_offline_core.AptOfflineCoreLib.guiBool = True
        
    def popupDirectoryDialog(self):
        # Popup a Directory selection box
        directory = QtGui.QFileDialog.getOpenFileName(self, u'Select the signature file')
        # Show the selected file path in the field marked for showing directory path
        self.ui.profileFilePath.setText(directory)
        
        self.ControlStartDownloadBox()
    
    def popupZipFileDialog(self):
        # Popup a Zip File selection box
        filename = QtGui.QFileDialog.getSaveFileName(self, u'Select the zip file to save downloads')
        # Show the selected file path in the field marked for showing directory path
        self.ui.zipFilePath.setText(filename)
        
        self.ControlStartDownloadBox()
        
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
        
        # TODO: check for zip file's presense
        self.zipfilepath = str(self.ui.zipFilePath.text())
        
        # if file has write permission
        if os.access(os.path.dirname(self.zipfilepath), os.W_OK) == False:
            if (len(self.zipfilepath) == 0):
                guicommon.updateInto (self.ui.rawLogHolder, 
                            guicommon.style("Please select a zip file to create archive!",'red'))
            else:
                guicommon.updateInto (self.ui.rawLogHolder, 
                    guicommon.style("%s does not have write access." % self.zipfilepath,'red'))
            return
        
        # if file already exists
        if os.path.exists(self.zipfilepath):
                ret = QMessageBox.warning(self, "Replace archive file?",
                   "The file %s already exists.\n"
                      "Do you want to overwrite it?" % self.zipfilepath,
                           QMessageBox.Yes | QMessageBox.No
                           , QMessageBox.Yes)
                if ret == QMessageBox.Yes:
                    # delete the file
                    try:
                        os.remove(self.zipfilepath)
                    except:
                        guicommon.updateInto (self.ui.rawLogHolder, 
                            guicommon.style("Could'nt write to %s!" % self.zipfilepath,'red'))
                else:
                    return
                   
        args = GetterArgs(filename=self.filepath, bundle_file= self.zipfilepath, progress_bar=self.ui.statusProgressBar, progress_label=self.ui.progressStatusDescription)
        
        #returnStatus = apt_offline_core.AptOfflineCoreLib.fetcher(args)
        # TODO: deal with return status laters
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

    def ControlStartDownloadBox(self):
        if self.ui.profileFilePath.text().isEmpty():
            self.ui.startDownloadButton.setEnabled(False)
        if self.ui.zipFilePath.text().isEmpty():
            self.ui.startDownloadButton.setEnabled(False)
        else:
            self.ui.startDownloadButton.setEnabled(True)
        

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtFetch()
    myapp.show()
    sys.exit(app.exec_())


