# -*- coding: utf-8 -*-
import os,sys
from PyQt5 import QtCore, QtGui, QtWidgets

import zipfile, tempfile

from apt_offline_gui.Ui_AptOfflineQtInstallChangelog import Ui_AptOfflineQtInstallChangelog

class AptOfflineQtInstallChangelog(QtWidgets.QDialog):
        output = QtCore.pyqtSignal(str)
        progress = QtCore.pyqtSignal(str, str)
        status = QtCore.pyqtSignal(str)
        finished = QtCore.pyqtSignal()
        terminated = QtCore.pyqtSignal()

        def __init__(self, filepath, parent=None):
            QtWidgets.QWidget.__init__(self, parent)
            self.ui = Ui_AptOfflineQtInstallChangelog()

            self.filepath = filepath

            self.ui.setupUi(self)
            self.populateChangelog(self.filepath)

            # Connect the clicked signal of the Browse button to it's slot
            #QtCore.QObject.connect(self.ui.closeButton, QtCore.SIGNAL("clicked()"),
            #                self.reject )
            self.ui.closeButton.clicked.connect(self.reject)

        def populateChangelog(self, path):

            self.chlogFile = tempfile.NamedTemporaryFile('r+', buffering=-1, encoding='utf-8', dir=None, delete=True)
            self.chlogPresent = False

            if os.path.isdir(path):
                for eachItem in os.listdir(path):
                    eachItem = os.path.join(path, eachItem)
                    if eachItem.endswith(".changelog"):
                        eachFile = open(eachItem, 'r')
                        self.chlogFile.write(eachFile.read())
                        self.chlogPresent = True
            elif os.path.isfile(path):
                zipLogFile = zipfile.ZipFile(path)
                for filename in zipLogFile.namelist():
                    if filename.endswith(".changelog"):
                        self.chlogFile.write(zipLogFile.read(filename))
                        self.chlogPresent = True
            else:
                return False

            if self.chlogPresent is False:
                self.ui.changelogPlainTextEdit.clear()
                self.ui.changelogPlainTextEdit.appendPlainText('No changelog present')
            else:
                self.ui.changelogPlainTextEdit.clear()
                self.chlogFile.seek(0)
                self.ui.changelogPlainTextEdit.appendPlainText(self.chlogFile.read())

                myCursor = self.ui.changelogPlainTextEdit.textCursor()
                myCursor.movePosition(myCursor.Start)
                self.ui.changelogPlainTextEdit.setTextCursor(myCursor)


if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        myapp = AptOfflineQtInstallChangelog()
        myapp.show()
        sys.exit(app.exec_())
