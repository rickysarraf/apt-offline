# -*- coding: utf-8 -*-
import os,sys
from PyQt4 import QtCore, QtGui

import zipfile, tempfile

from apt_offline_gui.Ui_AptOfflineQtInstallBugList import Ui_AptOfflineQtInstallBugList
import apt_offline_core.AptOfflineCoreLib as AptOfflineCoreLib

class AptOfflineQtInstallBugList(QtGui.QDialog):
        def __init__(self, filepath, parent=None):
            QtGui.QWidget.__init__(self, parent)
            self.ui = Ui_AptOfflineQtInstallBugList()
            
            self.bugList = {}
            self.filepath = filepath
            
            self.ui.setupUi(self)
            self.populateBugList(self.filepath)            
            
            self.ui.bugListViewWindow.itemSelectionChanged.connect(self.populateBugListPlainTextEdit)
            
            # Connect the clicked signal of the Browse button to it's slot
            QtCore.QObject.connect(self.ui.closeButton, QtCore.SIGNAL("clicked()"),
                            self.reject )

        def populateBugListPlainTextEdit(self):
                self.ui.bugListplainTextEdit.clear()
                textItem = str(self.ui.bugListViewWindow.currentItem().text() )
                
                extractedText = self.bugList[textItem]
                self.ui.bugListplainTextEdit.appendPlainText(" ".join(extractedText))
                
                myCursor = self.ui.bugListplainTextEdit.textCursor()
                myCursor.movePosition(myCursor.Start)
                self.ui.bugListplainTextEdit.setTextCursor(myCursor)

        def populateBugList(self, path):
                
                if os.path.isfile(path):
                        file = zipfile.ZipFile(path, "r")
                        
                        for filename in file.namelist():
                                if filename.endswith( AptOfflineCoreLib.apt_bug_file_format ):

                                        temp = tempfile.NamedTemporaryFile()
                                        temp.file.write( file.read( filename ) )
                                        temp.file.flush()
                                        temp.file.seek( 0 ) #Let's go back to the start of the file
                                        for bug_subject_identifier in temp.file.readlines():
                                                if bug_subject_identifier.startswith( '#' ):
                                                        bug_subject_identifier = bug_subject_identifier.rstrip("\n")
                                                        temp.file.seek(0)
                                                        self.bugList[bug_subject_identifier] = temp.file.readlines()
                                                        break
                                        temp.file.close()
                                        
                        for eachItem in self.bugList.keys():
                                item = QtGui.QListWidgetItem(eachItem)
                                self.ui.bugListViewWindow.addItem(item)        

                elif os.path.isdir(path):
                        print "Do something"
                else:
                        print "Invalid Path"
                        return False
                    
#    def StartInstall(self):
#         gui validation
#         Clear the consoleOutputHolder
#        self.ui.rawLogHolder.setText("")
#
#        self.filepath = str(self.ui.zipFilePath.text())
#
#        if os.path.isfile(self.filepath) == False:
#            if (len(self.filepath) == 0):
#                self.ui.rawLogHolder.setText ( \
#                    guicommon.style("Please select a zip file!",'red'))
#            else:
#                self.ui.rawLogHolder.setText ( \
#                    guicommon.style("%s does not exist." % self.filepath,'red'))
#            return
#
#         parse args
#        args = InstallerArgs(filename=self.filepath, progress_bar=self.ui.statusProgressBar, progress_label=self.ui.progressStatusDescription )
#
#        self.disableActions()
#        self.ui.progressStatusDescription.setText("Syncing updates")
#        self.worker.setArgs (args)
#        self.worker.start()
#
#    def popupDirectoryDialog(self):
#         Popup a Directory selection box
#        directory = QtGui.QFileDialog.getOpenFileName(self, u'Select the Zip File')
#         Show the selected file path in the field marked for showing directory path
#        self.ui.zipFilePath.setText(directory)
#        self.ui.zipFilePath.setFocus()
#    
#    def ControlStartInstallBox(self):
#        if self.ui.zipFilePath.text().isEmpty():
#            self.ui.startInstallButton.setEnabled(False)
#        else:
#            self.ui.startInstallButton.setEnabled(True)
#            
#    def updateLog(self,text):
#        guicommon.updateInto (self.ui.rawLogHolder,text)
#
#    def updateStatus(self,text):
#         status handler
#        self.ui.progressStatusDescription.setText(text)
#
#    def updateProgress(self,progress,total):
#        try:
#             try parsing numbers and updating progressBar
#            percent = (float(progress)/float(total))*100
#            self.ui.statusProgressBar.setValue (percent)
#        except:
#             ''' nothing to do '''
#
#    def finishedWork(self):
#        self.enableActions()
#        guicommon.updateInto (self.ui.rawLogHolder,
#            guicommon.style("Finished syncting updates/packages","green_fin"))
#        self.ui.progressStatusDescription.setText("Finished Syncing")
#        
#    def disableActions(self):
#        self.ui.cancelButton.setEnabled(False)
#        self.ui.startInstallButton.setEnabled(False)
#        self.ui.browseFilePathButton.setEnabled(False)
#        self.ui.zipFilePath.setEnabled(False)
#
#    def enableActions(self):
#        self.ui.cancelButton.setEnabled(True)
#        self.ui.startInstallButton.setEnabled(True)
#        self.ui.browseFilePathButton.setEnabled(True)
#        self.ui.zipFilePath.setEnabled(True)

if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        myapp = AptOfflineQtInstallBugList()
        myapp.show()
        sys.exit(app.exec_())
