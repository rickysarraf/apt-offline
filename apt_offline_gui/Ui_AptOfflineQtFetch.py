# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtFetch.ui'
#
# Created: Thu Feb  4 01:36:22 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AptOfflineQtFetch(object):
    def setupUi(self, AptOfflineQtFetch):
        AptOfflineQtFetch.setObjectName("AptOfflineQtFetch")
        AptOfflineQtFetch.setWindowModality(QtCore.Qt.WindowModal)
        AptOfflineQtFetch.resize(466, 463)
        self.profileFilePath = QtGui.QLineEdit(AptOfflineQtFetch)
        self.profileFilePath.setGeometry(QtCore.QRect(30, 60, 270, 30))
        self.profileFilePath.setObjectName("profileFilePath")
        self.browseFilePathButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.browseFilePathButton.setGeometry(QtCore.QRect(320, 60, 110, 30))
        self.browseFilePathButton.setObjectName("browseFilePathButton")
        self.startDownloadButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.startDownloadButton.setEnabled(False)
        self.startDownloadButton.setGeometry(QtCore.QRect(90, 110, 130, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/go-down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.startDownloadButton.setIcon(icon)
        self.startDownloadButton.setCheckable(False)
        self.startDownloadButton.setChecked(False)
        self.startDownloadButton.setFlat(False)
        self.startDownloadButton.setObjectName("startDownloadButton")
        self.cancelButton = QtGui.QPushButton(AptOfflineQtFetch)
        self.cancelButton.setGeometry(QtCore.QRect(240, 110, 140, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")
        self.label = QtGui.QLabel(AptOfflineQtFetch)
        self.label.setGeometry(QtCore.QRect(30, 30, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.statusProgressBar = QtGui.QProgressBar(AptOfflineQtFetch)
        self.statusProgressBar.setGeometry(QtCore.QRect(30, 190, 410, 20))
        self.statusProgressBar.setProperty("value", QtCore.QVariant(0))
        self.statusProgressBar.setObjectName("statusProgressBar")
        self.rawLogHolder = QtGui.QPlainTextEdit(AptOfflineQtFetch)
        self.rawLogHolder.setGeometry(QtCore.QRect(30, 230, 410, 210))
        self.rawLogHolder.setObjectName("rawLogHolder")
        self.label_2 = QtGui.QLabel(AptOfflineQtFetch)
        self.label_2.setGeometry(QtCore.QRect(40, 170, 70, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.progressStatusDescription = QtGui.QLabel(AptOfflineQtFetch)
        self.progressStatusDescription.setGeometry(QtCore.QRect(90, 170, 53, 15))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressStatusDescription.setFont(font)
        self.progressStatusDescription.setObjectName("progressStatusDescription")

        self.retranslateUi(AptOfflineQtFetch)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtFetch)

    def retranslateUi(self, AptOfflineQtFetch):
        AptOfflineQtFetch.setWindowTitle(QtGui.QApplication.translate("AptOfflineQtFetch", "Fetch Packages or Upgrade", None, QtGui.QApplication.UnicodeUTF8))
        self.browseFilePathButton.setText(QtGui.QApplication.translate("AptOfflineQtFetch", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.startDownloadButton.setText(QtGui.QApplication.translate("AptOfflineQtFetch", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("AptOfflineQtFetch", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AptOfflineQtFetch", "Select the profile file", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AptOfflineQtFetch", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.progressStatusDescription.setText(QtGui.QApplication.translate("AptOfflineQtFetch", "Ready", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
