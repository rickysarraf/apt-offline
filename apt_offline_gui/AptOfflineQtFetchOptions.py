import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets

from apt_offline_gui.Ui_AptOfflineQtFetchOptions import Ui_downloadOptionsDialog

class AptOfflineQtFetchOptions(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_downloadOptionsDialog()
        self.ui.setupUi(self)

        # Connect the clicked signal of the Ok button to it's slot
        #QtCore.QObject.connect(self.ui.downloadOptionDialogOkButton, QtCore.SIGNAL("clicked()"),
        #                self.validateOptions )
        self.ui.downloadOptionDialogOkButton.clicked.connect(self.validateOptions)

        #QtCore.QObject.connect(self.ui.useProxyCheckBox, QtCore.SIGNAL("toggled(bool)"),
        #                self.toggleProxyControls )
        self.ui.useProxyCheckBox.toggled.connect(self.toggleProxyControls)

        #QtCore.QObject.connect(self.ui.cacheDirBrowseButton, QtCore.SIGNAL("clicked()"),
        #                self.populateCacheDir )
        self.ui.cacheDirBrowseButton.clicked.connect(self.populateCacheDir)

        # defaults
        self.num_of_threads = 1
        self.socket_timeout = 30
        self.cache_dir = None
        self.disable_md5check = False
        self.deb_bugs = False
        self.proxy_host = None
        self.proxy_port = None

    def storeOptions(self):

            self._num_of_threads = self.ui.spinThreads.value()
            self._socket_timeout = self.ui.spinTimeout.value()

            self._cache_dir = str(self.ui.cacheDirLineEdit.text() )

            self._disable_md5check = self.ui.disableChecksumCheckBox.isChecked()
            self._deb_bugs = self.ui.fetchBugReportsCheckBox.isChecked()

            if self.ui.useProxyCheckBox.isChecked():
                    self._proxy_host = str(self.ui.proxyHostLineEdit.text() )
                    self._proxy_port = str(self.ui.proxyPortLineEdit.text() )
            else:
                    self._proxy_host = None
                    self._proxy_port = None

    def validateOptions(self):
            self.storeOptions()

            if len(self._cache_dir) > 0 and not (os.access(self._cache_dir, os.W_OK) or os.access(self._cache_dir, os.R_OK) ):
                    QtWidgets.QMessageBox.critical(self, "Error", "Could not locate cache directory")
                    return

            if self._proxy_port:
                    try:
                            int(self._proxy_port)
                    except:
                            QtWidgets.QMessageBox.critical(self, "Error", "Invalid Proxy Port Number")
                            return
            self.applyOptionValues()
            self.hide()

    def applyOptionValues(self):
            self.num_of_threads = self._num_of_threads
            self.socket_timeout = self._socket_timeout

            self.cache_dir = self._cache_dir

            self.disable_md5check = self._disable_md5check
            self.deb_bugs = self._deb_bugs

            self.proxy_host = self._proxy_host
            self.proxy_port = self._proxy_port

    def toggleProxyControls(self):
            if self.ui.useProxyCheckBox.isChecked():
                    self.ui.proxyHostLineEdit.setEnabled(True)
                    self.ui.proxyPortLineEdit.setEnabled(True)
            else:
                    self.ui.proxyHostLineEdit.setEnabled(False)
                    self.ui.proxyPortLineEdit.setEnabled(False)


    def populateCacheDir(self):
            directory = QtWidgets.QFileDialog.getExistingDirectory(None, 'Provide path to APT\'s Cache Dir')
            self.ui.cacheDirLineEdit.setText(directory)
            self._cache_dir = directory


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtFetchOptions()
    myapp.show()
    sys.exit(app.exec_())
