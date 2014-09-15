# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtFetchOptions.ui'
#
# Created: Sat Sep 13 15:37:48 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_downloadOptionsDialog(object):
    def setupUi(self, downloadOptionsDialog):
        downloadOptionsDialog.setObjectName(_fromUtf8("downloadOptionsDialog"))
        downloadOptionsDialog.resize(443, 304)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(downloadOptionsDialog.sizePolicy().hasHeightForWidth())
        downloadOptionsDialog.setSizePolicy(sizePolicy)
        downloadOptionsDialog.setMinimumSize(QtCore.QSize(443, 304))
        downloadOptionsDialog.setMaximumSize(QtCore.QSize(443, 304))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/configure.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        downloadOptionsDialog.setWindowIcon(icon)
        downloadOptionsDialog.setSizeGripEnabled(False)
        downloadOptionsDialog.setModal(True)
        self.lblThreads = QtGui.QLabel(downloadOptionsDialog)
        self.lblThreads.setGeometry(QtCore.QRect(300, 10, 81, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblThreads.setFont(font)
        self.lblThreads.setObjectName(_fromUtf8("lblThreads"))
        self.spinThreads = QtGui.QSpinBox(downloadOptionsDialog)
        self.spinThreads.setGeometry(QtCore.QRect(390, 9, 40, 30))
        self.spinThreads.setMinimum(1)
        self.spinThreads.setMaximum(10)
        self.spinThreads.setObjectName(_fromUtf8("spinThreads"))
        self.downloadOptionDialogOkButton = QtGui.QPushButton(downloadOptionsDialog)
        self.downloadOptionDialogOkButton.setGeometry(QtCore.QRect(350, 260, 81, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/dialog-ok-apply.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.downloadOptionDialogOkButton.setIcon(icon1)
        self.downloadOptionDialogOkButton.setObjectName(_fromUtf8("downloadOptionDialogOkButton"))
        self.lblSocketTimeo = QtGui.QLabel(downloadOptionsDialog)
        self.lblSocketTimeo.setGeometry(QtCore.QRect(10, 8, 111, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblSocketTimeo.setFont(font)
        self.lblSocketTimeo.setObjectName(_fromUtf8("lblSocketTimeo"))
        self.spinTimeout = QtGui.QSpinBox(downloadOptionsDialog)
        self.spinTimeout.setGeometry(QtCore.QRect(150, 7, 51, 30))
        self.spinTimeout.setMinimum(10)
        self.spinTimeout.setMaximum(100)
        self.spinTimeout.setProperty("value", 30)
        self.spinTimeout.setObjectName(_fromUtf8("spinTimeout"))
        self.cacheDirLineEdit = QtGui.QLineEdit(downloadOptionsDialog)
        self.cacheDirLineEdit.setGeometry(QtCore.QRect(150, 60, 191, 31))
        self.cacheDirLineEdit.setObjectName(_fromUtf8("cacheDirLineEdit"))
        self.cacheDirBrowseButton = QtGui.QPushButton(downloadOptionsDialog)
        self.cacheDirBrowseButton.setGeometry(QtCore.QRect(350, 60, 81, 31))
        self.cacheDirBrowseButton.setObjectName(_fromUtf8("cacheDirBrowseButton"))
        self.lblCacheDir = QtGui.QLabel(downloadOptionsDialog)
        self.lblCacheDir.setGeometry(QtCore.QRect(10, 60, 141, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblCacheDir.setFont(font)
        self.lblCacheDir.setObjectName(_fromUtf8("lblCacheDir"))
        self.disableChecksumCheckBox = QtGui.QCheckBox(downloadOptionsDialog)
        self.disableChecksumCheckBox.setGeometry(QtCore.QRect(10, 120, 151, 31))
        self.disableChecksumCheckBox.setObjectName(_fromUtf8("disableChecksumCheckBox"))
        self.fetchBugReportsCheckBox = QtGui.QCheckBox(downloadOptionsDialog)
        self.fetchBugReportsCheckBox.setGeometry(QtCore.QRect(180, 120, 151, 31))
        self.fetchBugReportsCheckBox.setObjectName(_fromUtf8("fetchBugReportsCheckBox"))
        self.proxyGroupBox = QtGui.QGroupBox(downloadOptionsDialog)
        self.proxyGroupBox.setGeometry(QtCore.QRect(10, 170, 441, 80))
        self.proxyGroupBox.setStyleSheet(_fromUtf8(""))
        self.proxyGroupBox.setTitle(_fromUtf8(""))
        self.proxyGroupBox.setFlat(True)
        self.proxyGroupBox.setObjectName(_fromUtf8("proxyGroupBox"))
        self.proxyHostLineEdit = QtGui.QLineEdit(self.proxyGroupBox)
        self.proxyHostLineEdit.setEnabled(False)
        self.proxyHostLineEdit.setGeometry(QtCore.QRect(25, 39, 238, 31))
        self.proxyHostLineEdit.setObjectName(_fromUtf8("proxyHostLineEdit"))
        self.proxyPortLineEdit = QtGui.QLineEdit(self.proxyGroupBox)
        self.proxyPortLineEdit.setEnabled(False)
        self.proxyPortLineEdit.setGeometry(QtCore.QRect(280, 39, 61, 31))
        self.proxyPortLineEdit.setText(_fromUtf8(""))
        self.proxyPortLineEdit.setObjectName(_fromUtf8("proxyPortLineEdit"))
        self.useProxyCheckBox = QtGui.QCheckBox(self.proxyGroupBox)
        self.useProxyCheckBox.setGeometry(QtCore.QRect(0, 0, 89, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.useProxyCheckBox.setFont(font)
        self.useProxyCheckBox.setObjectName(_fromUtf8("useProxyCheckBox"))
        self.lblProxyPort = QtGui.QLabel(downloadOptionsDialog)
        self.lblProxyPort.setGeometry(QtCore.QRect(290, 186, 138, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblProxyPort.setFont(font)
        self.lblProxyPort.setObjectName(_fromUtf8("lblProxyPort"))
        self.lblProxyHost = QtGui.QLabel(downloadOptionsDialog)
        self.lblProxyHost.setGeometry(QtCore.QRect(35, 186, 138, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblProxyHost.setFont(font)
        self.lblProxyHost.setObjectName(_fromUtf8("lblProxyHost"))

        self.retranslateUi(downloadOptionsDialog)
        QtCore.QMetaObject.connectSlotsByName(downloadOptionsDialog)

    def retranslateUi(self, downloadOptionsDialog):
        downloadOptionsDialog.setWindowTitle(_translate("downloadOptionsDialog", "Advanced options for download", None))
        self.lblThreads.setToolTip(_translate("downloadOptionsDialog", "Number of parallel connections", None))
        self.lblThreads.setText(_translate("downloadOptionsDialog", "Use threads", None))
        self.spinThreads.setToolTip(_translate("downloadOptionsDialog", "Number of parallel connections", None))
        self.downloadOptionDialogOkButton.setText(_translate("downloadOptionsDialog", "Ok", None))
        self.lblSocketTimeo.setToolTip(_translate("downloadOptionsDialog", "Nework timeout in seconds", None))
        self.lblSocketTimeo.setText(_translate("downloadOptionsDialog", "Network Timeout", None))
        self.spinTimeout.setToolTip(_translate("downloadOptionsDialog", "Nework timeout in seconds", None))
        self.cacheDirLineEdit.setToolTip(_translate("downloadOptionsDialog", "Cache folder to search for", None))
        self.cacheDirBrowseButton.setText(_translate("downloadOptionsDialog", "Browse", None))
        self.lblCacheDir.setToolTip(_translate("downloadOptionsDialog", "Cache folder to search for", None))
        self.lblCacheDir.setText(_translate("downloadOptionsDialog", "Cache Directory", None))
        self.disableChecksumCheckBox.setToolTip(_translate("downloadOptionsDialog", "Disables checksum verification of downloaded items. Enable only if you know what you are doing", None))
        self.disableChecksumCheckBox.setText(_translate("downloadOptionsDialog", "Disable Checksum", None))
        self.fetchBugReportsCheckBox.setToolTip(_translate("downloadOptionsDialog", "Fetch Bug Reports", None))
        self.fetchBugReportsCheckBox.setText(_translate("downloadOptionsDialog", "Fetch Bug Reports", None))
        self.proxyHostLineEdit.setToolTip(_translate("downloadOptionsDialog", "Proxy Server Host/IP Address", None))
        self.proxyPortLineEdit.setToolTip(_translate("downloadOptionsDialog", "Proxy Server Port Address", None))
        self.useProxyCheckBox.setText(_translate("downloadOptionsDialog", "Proxy", None))
        self.lblProxyPort.setToolTip(_translate("downloadOptionsDialog", "Cache folder to search for", None))
        self.lblProxyPort.setText(_translate("downloadOptionsDialog", "Port", None))
        self.lblProxyHost.setToolTip(_translate("downloadOptionsDialog", "Cache folder to search for", None))
        self.lblProxyHost.setText(_translate("downloadOptionsDialog", "Host", None))

import resources_rc
