# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtFetch.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_AptOfflineQtFetch(object):
    def setupUi(self, AptOfflineQtFetch):
        AptOfflineQtFetch.setObjectName(_fromUtf8("AptOfflineQtFetch"))
        AptOfflineQtFetch.setWindowModality(QtCore.Qt.ApplicationModal)
        AptOfflineQtFetch.resize(468, 483)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineQtFetch.sizePolicy().hasHeightForWidth())
        AptOfflineQtFetch.setSizePolicy(sizePolicy)
        AptOfflineQtFetch.setMinimumSize(QtCore.QSize(468, 475))
        AptOfflineQtFetch.setMaximumSize(QtCore.QSize(468, 495))
        self.profileFilePath = QtGui.QLineEdit(AptOfflineQtFetch)
        self.profileFilePath.setGeometry(QtCore.QRect(30, 35, 270, 30))
        self.profileFilePath.setObjectName(_fromUtf8("profileFilePath"))
        self.browseFilePathButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.browseFilePathButton.setGeometry(QtCore.QRect(320, 35, 110, 30))
        self.browseFilePathButton.setObjectName(_fromUtf8("browseFilePathButton"))
        self.startDownloadButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.startDownloadButton.setEnabled(False)
        self.startDownloadButton.setGeometry(QtCore.QRect(179, 148, 120, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/go-down.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.startDownloadButton.setIcon(icon)
        self.startDownloadButton.setShortcut(_fromUtf8(""))
        self.startDownloadButton.setCheckable(False)
        self.startDownloadButton.setChecked(False)
        self.startDownloadButton.setFlat(False)
        self.startDownloadButton.setObjectName(_fromUtf8("startDownloadButton"))
        self.cancelButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.cancelButton.setGeometry(QtCore.QRect(319, 148, 111, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/application-exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.lblSelectSig = QtGui.QLabel(AptOfflineQtFetch)
        self.lblSelectSig.setGeometry(QtCore.QRect(30, 5, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblSelectSig.setFont(font)
        self.lblSelectSig.setObjectName(_fromUtf8("lblSelectSig"))
        self.statusProgressBar = QtGui.QProgressBar(AptOfflineQtFetch)
        self.statusProgressBar.setGeometry(QtCore.QRect(30, 214, 410, 20))
        self.statusProgressBar.setProperty("value", 0)
        self.statusProgressBar.setObjectName(_fromUtf8("statusProgressBar"))
        self.lblStatus = QtGui.QLabel(AptOfflineQtFetch)
        self.lblStatus.setGeometry(QtCore.QRect(32, 194, 70, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblStatus.setFont(font)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.progressStatusDescription = QtGui.QLabel(AptOfflineQtFetch)
        self.progressStatusDescription.setGeometry(QtCore.QRect(82, 194, 341, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressStatusDescription.setFont(font)
        self.progressStatusDescription.setObjectName(_fromUtf8("progressStatusDescription"))
        self.rawLogHolder = QtGui.QTextEdit(AptOfflineQtFetch)
        self.rawLogHolder.setGeometry(QtCore.QRect(30, 252, 411, 211))
        self.rawLogHolder.setAcceptDrops(False)
        self.rawLogHolder.setReadOnly(True)
        self.rawLogHolder.setObjectName(_fromUtf8("rawLogHolder"))
        self.browseZipFileButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.browseZipFileButton.setGeometry(QtCore.QRect(320, 98, 110, 30))
        self.browseZipFileButton.setObjectName(_fromUtf8("browseZipFileButton"))
        self.lblSaveAs = QtGui.QLabel(AptOfflineQtFetch)
        self.lblSaveAs.setGeometry(QtCore.QRect(30, 68, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblSaveAs.setFont(font)
        self.lblSaveAs.setObjectName(_fromUtf8("lblSaveAs"))
        self.zipFilePath = QtGui.QLineEdit(AptOfflineQtFetch)
        self.zipFilePath.setGeometry(QtCore.QRect(30, 98, 270, 30))
        self.zipFilePath.setObjectName(_fromUtf8("zipFilePath"))
        self.advancedOptionsButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.advancedOptionsButton.setEnabled(True)
        self.advancedOptionsButton.setGeometry(QtCore.QRect(31, 148, 131, 30))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/configure.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.advancedOptionsButton.setIcon(icon2)
        self.advancedOptionsButton.setShortcut(_fromUtf8(""))
        self.advancedOptionsButton.setCheckable(False)
        self.advancedOptionsButton.setChecked(False)
        self.advancedOptionsButton.setFlat(False)
        self.advancedOptionsButton.setObjectName(_fromUtf8("advancedOptionsButton"))
        self.saveDatacheckBox = QtGui.QCheckBox(AptOfflineQtFetch)
        self.saveDatacheckBox.setGeometry(QtCore.QRect(321, 80, 110, 18))
        self.saveDatacheckBox.setObjectName(_fromUtf8("saveDatacheckBox"))

        self.retranslateUi(AptOfflineQtFetch)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtFetch)
        AptOfflineQtFetch.setTabOrder(self.profileFilePath, self.browseFilePathButton)
        AptOfflineQtFetch.setTabOrder(self.browseFilePathButton, self.zipFilePath)
        AptOfflineQtFetch.setTabOrder(self.zipFilePath, self.saveDatacheckBox)
        AptOfflineQtFetch.setTabOrder(self.saveDatacheckBox, self.browseZipFileButton)
        AptOfflineQtFetch.setTabOrder(self.browseZipFileButton, self.advancedOptionsButton)
        AptOfflineQtFetch.setTabOrder(self.advancedOptionsButton, self.startDownloadButton)
        AptOfflineQtFetch.setTabOrder(self.startDownloadButton, self.cancelButton)
        AptOfflineQtFetch.setTabOrder(self.cancelButton, self.rawLogHolder)

    def retranslateUi(self, AptOfflineQtFetch):
        AptOfflineQtFetch.setWindowTitle(_translate("AptOfflineQtFetch", "Fetch Packages or Updates", None))
        self.browseFilePathButton.setText(_translate("AptOfflineQtFetch", "Browse", None))
        self.startDownloadButton.setText(_translate("AptOfflineQtFetch", "Download", None))
        self.cancelButton.setText(_translate("AptOfflineQtFetch", "Close", None))
        self.lblSelectSig.setText(_translate("AptOfflineQtFetch", "Select the signature file", None))
        self.lblStatus.setText(_translate("AptOfflineQtFetch", "Status:", None))
        self.progressStatusDescription.setText(_translate("AptOfflineQtFetch", "Ready", None))
        self.browseZipFileButton.setText(_translate("AptOfflineQtFetch", "Browse", None))
        self.lblSaveAs.setText(_translate("AptOfflineQtFetch", "Save data as", None))
        self.advancedOptionsButton.setToolTip(_translate("AptOfflineQtFetch", "Additional options for download", None))
        self.advancedOptionsButton.setText(_translate("AptOfflineQtFetch", "Options", None))
        self.saveDatacheckBox.setText(_translate("AptOfflineQtFetch", "Is Directory", None))

import resources_rc
