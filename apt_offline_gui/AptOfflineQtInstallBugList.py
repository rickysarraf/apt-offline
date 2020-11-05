# -*- coding: utf-8 -*-
import os,sys
from PyQt5 import QtCore, QtGui, QtWidgets

import zipfile, tempfile

from apt_offline_gui.Ui_AptOfflineQtInstallBugList import Ui_AptOfflineQtInstallBugList
import apt_offline_core.AptOfflineCoreLib as AptOfflineCoreLib

class AptOfflineQtInstallBugList(QtWidgets.QDialog):
        output = QtCore.pyqtSignal(str)
        progress = QtCore.pyqtSignal(str, str)
        status = QtCore.pyqtSignal(str)
        finished = QtCore.pyqtSignal()
        terminated = QtCore.pyqtSignal()

        def __init__(self, filepath, parent=None):
            """
            Initializes the tooltip.

            Args:
                self: (todo): write your description
                filepath: (str): write your description
                parent: (todo): write your description
            """
            QtWidgets.QWidget.__init__(self, parent)
            self.ui = Ui_AptOfflineQtInstallBugList()

            self.bugList = {}
            self.filepath = filepath

            self.ui.setupUi(self)
            self.populateBugList(self.filepath)

            self.ui.bugListViewWindow.itemSelectionChanged.connect(self.populateBugListPlainTextEdit)

            # Connect the clicked signal of the Browse button to it's slot
            #QtCore.QObject.connect(self.ui.closeButton, QtCore.SIGNAL("clicked()"),
            #                self.reject )
            self.ui.closeButton.clicked.connect(self.reject)

        def populateBugListPlainTextEdit(self):
            """
            Populate the currently selected text.

            Args:
                self: (todo): write your description
            """
                self.ui.bugListplainTextEdit.clear()
                textItem = str(self.ui.bugListViewWindow.currentItem().text() )

                extractedText = self.bugList[textItem]
                self.ui.bugListplainTextEdit.appendPlainText(" ".join(extractedText))

                myCursor = self.ui.bugListplainTextEdit.textCursor()
                myCursor.movePosition(myCursor.Start)
                self.ui.bugListplainTextEdit.setTextCursor(myCursor)

        def noBugPopulateBugListPlainTextEdit(self):
            """
            Updates the text for the current text.

            Args:
                self: (todo): write your description
            """
                self.ui.bugListplainTextEdit.clear()
                self.ui.bugListplainTextEdit.appendPlainText("No Bug Reports Found")

        def populateBugList(self, path):
            """
            Populate a list of files.

            Args:
                self: (todo): write your description
                path: (str): write your description
            """

                if os.path.isfile(path):
                        zipFile = zipfile.ZipFile(path, "r")

                        for filename in zipFile.namelist():
                                if filename.endswith( AptOfflineCoreLib.apt_bug_file_format ):
                                        #INFO: The splitter is use is "{}". Also used at other places
                                        bugNumber = filename.split("{}")[1]

                                        temp = tempfile.NamedTemporaryFile()
                                        temp.file.write( zipFile.read( filename ) )
                                        temp.file.flush()
                                        temp.file.seek( 0 ) #Let's go back to the start of the file
                                        for bug_subject_identifier in temp.file.readlines():
                                                if bug_subject_identifier.startswith( 'Subject:' ):
                                                        bug_subject_identifier = str(bugNumber) + ": " + bug_subject_identifier.lstrip("Subject:")
                                                        bug_subject_identifier = bug_subject_identifier.rstrip("\n")
                                                        temp.file.seek(0)
                                                        self.bugList[bug_subject_identifier] = temp.file.readlines()
                                                        break
                                        temp.file.close()

                elif os.path.isdir(path):
                        for filename in os.listdir( path ):
                                if filename.endswith( AptOfflineCoreLib.apt_bug_file_format ):
                                        bugNumber = filename.split("{}")[1]
                                        filename = os.path.join(path, filename)
                                        temp = open(filename, 'r')
                                        for bug_subject_identifier in temp.readlines():
                                                if bug_subject_identifier.startswith( 'Subject:' ):
                                                        bug_subject_identifier = str(bugNumber) + ": " + bug_subject_identifier.lstrip("Subject:")
                                                        bug_subject_identifier = bug_subject_identifier.rstrip("\n")
                                                        temp.seek(0)
                                                        self.bugList[bug_subject_identifier] = temp.readlines()
                                                        break
                                        temp.close()
                else:
                        print("Invalid Path")
                        return False

                if len(list(self.bugList.keys())) == 0:
                        self.noBugPopulateBugListPlainTextEdit()
                else:
                        for eachItem in list(self.bugList.keys()):
                                item = QtGui.QListWidgetItem(eachItem)
                                self.ui.bugListViewWindow.addItem(item)


if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        myapp = AptOfflineQtInstallBugList()
        myapp.show()
        sys.exit(app.exec_())
