# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtInstall.ui'
#
# Created: Sat Mar  6 20:54:12 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AptOfflineQtInstall(object):
    def setupUi(self, AptOfflineQtInstall):
        AptOfflineQtInstall.setObjectName("AptOfflineQtInstall")
        AptOfflineQtInstall.setWindowModality(QtCore.Qt.WindowModal)
        AptOfflineQtInstall.resize(466, 440)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineQtInstall.sizePolicy().hasHeightForWidth())
        AptOfflineQtInstall.setSizePolicy(sizePolicy)
        AptOfflineQtInstall.setMinimumSize(QtCore.QSize(466, 440))
        AptOfflineQtInstall.setMaximumSize(QtCore.QSize(466, 440))
        self.zipFilePath = QtGui.QLineEdit(AptOfflineQtInstall)
        self.zipFilePath.setGeometry(QtCore.QRect(30, 43, 270, 30))
        self.zipFilePath.setObjectName("zipFilePath")
        self.browseFilePathButton = QtGui.QPushButton(AptOfflineQtInstall)
        self.browseFilePathButton.setGeometry(QtCore.QRect(320, 43, 110, 30))
        self.browseFilePathButton.setObjectName("browseFilePathButton")
        self.startInstallButton = QtGui.QPushButton(AptOfflineQtInstall)
        self.startInstallButton.setEnabled(False)
        self.startInstallButton.setGeometry(QtCore.QRect(90, 93, 130, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/dialog-ok-apply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.startInstallButton.setIcon(icon)
        self.startInstallButton.setObjectName("startInstallButton")
        self.cancelButton = QtGui.QPushButton(AptOfflineQtInstall)
        self.cancelButton.setGeometry(QtCore.QRect(240, 93, 140, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")
        self.statusProgressBar = QtGui.QProgressBar(AptOfflineQtInstall)
        self.statusProgressBar.setGeometry(QtCore.QRect(30, 161, 410, 20))
        self.statusProgressBar.setProperty("value", 0)
        self.statusProgressBar.setObjectName("statusProgressBar")
        self.label = QtGui.QLabel(AptOfflineQtInstall)
        self.label.setGeometry(QtCore.QRect(30, 13, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(AptOfflineQtInstall)
        self.label_2.setGeometry(QtCore.QRect(40, 141, 70, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.progressStatusDescription = QtGui.QLabel(AptOfflineQtInstall)
        self.progressStatusDescription.setGeometry(QtCore.QRect(90, 141, 53, 15))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressStatusDescription.setFont(font)
        self.progressStatusDescription.setObjectName("progressStatusDescription")
        self.rawLogHolder = QtGui.QTextEdit(AptOfflineQtInstall)
        self.rawLogHolder.setGeometry(QtCore.QRect(30, 201, 411, 221))
        self.rawLogHolder.setObjectName("rawLogHolder")

        self.retranslateUi(AptOfflineQtInstall)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtInstall)

    def retranslateUi(self, AptOfflineQtInstall):
        AptOfflineQtInstall.setWindowTitle(QtGui.QApplication.translate("AptOfflineQtInstall", "Install Packages", None, QtGui.QApplication.UnicodeUTF8))
        self.browseFilePathButton.setText(QtGui.QApplication.translate("AptOfflineQtInstall", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.startInstallButton.setText(QtGui.QApplication.translate("AptOfflineQtInstall", "Install", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("AptOfflineQtInstall", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AptOfflineQtInstall", "Select the zip file", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("AptOfflineQtInstall", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.progressStatusDescription.setText(QtGui.QApplication.translate("AptOfflineQtInstall", "Ready", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
