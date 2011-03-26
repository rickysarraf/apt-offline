import sys, os
import tempfile
from PyQt4 import QtCore, QtGui

from apt_offline_gui.Ui_AptOfflineQtFetchOptions import Ui_downloadOptionsDialog

class AptOfflineQtFetchOptions(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_downloadOptionsDialog()
        self.ui.setupUi(self)
        self.tempdir = tempfile.gettempdir()
        self.ui.tempDirLineEdit.setText(self.tempdir)
        
        # Connect the clicked signal of the Ok button to it's slot
        QtCore.QObject.connect(self.ui.downloadOptionDialogOkButton, QtCore.SIGNAL("clicked()"),
                        self.validateOptions )
        
        QtCore.QObject.connect(self.ui.useProxyCheckBox, QtCore.SIGNAL("toggled(bool)"),
                        self.toggleProxyControls )
        
        # Connect the clicked signal of the Browse button to it's slot
        QtCore.QObject.connect(self.ui.tempDirBrowseButton, QtCore.SIGNAL("clicked()"),
                        self.populateTempDir )
        
        QtCore.QObject.connect(self.ui.cacheDirBrowseButton, QtCore.SIGNAL("clicked()"),
                        self.populateCacheDir )
        
        # defaults
        self.num_of_threads = 1
        self.socket_timeout = 30
        self.cache_dir = None
        self.download_dir = None
        self.disable_md5check = False
        self.deb_bugs = False
        self.proxy_host = None
        self.proxy_port = None
    
    def storeOptions(self):
            
            self._num_of_threads = self.ui.spinThreads.value()
            self._socket_timeout = self.ui.spinTimeout.value()
            
            self._cache_dir = str(self.ui.cacheDirLineEdit.text() )
            self._download_dir = str(self.ui.tempDirLineEdit.text() )
            
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
                    QtGui.QMessageBox.critical(self, "Error", "Could not locate cache directory")
                    return
            
            if len(self._download_dir) > 0 and not os.access(self._download_dir, os.W_OK) :
                    QtGui.QMessageBox.critical(self, "Error", "Could not locate temporary download directory or invalid permissions")
                    return
                    
            if self._proxy_port:
                    try:
                            int(self._proxy_port)
                    except:
                            QtGui.QMessageBox.critical(self, "Error", "Invalid Proxy Port Number")
                            return
            self.applyOptionValues()
            self.hide()
                            
    def applyOptionValues(self):
            self.num_of_threads = self._num_of_threads
            self.socket_timeout = self._socket_timeout
            
            self.cache_dir = self._cache_dir
            self.download_dir = self._download_dir
            
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
                    
    def populateTempDir(self):
            directory = QtGui.QFileDialog.getExistingDirectory(None, u'Temporary directory to store data')
            self.ui.tempDirLineEdit.setText(directory)
            self._download_dir = directory
            
    def populateCacheDir(self):
            directory = QtGui.QFileDialog.getExistingDirectory(None, u'Provide path to APT\'s Cache Dir')
            self.ui.cacheDirLineEdit.setText(directory)
            self._cache_dir = directory
            
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = AptOfflineQtFetchOptions()
    myapp.show()
    sys.exit(app.exec_())
