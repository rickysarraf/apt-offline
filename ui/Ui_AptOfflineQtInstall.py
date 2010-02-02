# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtInstall.ui'
#
# Created: Tue Feb  2 23:59:58 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QAptOfflineInstall(object):
    def setupUi(self, QAptOfflineInstall):
        QAptOfflineInstall.setObjectName("QAptOfflineInstall")
        QAptOfflineInstall.setWindowModality(QtCore.Qt.WindowModal)
        QAptOfflineInstall.resize(466, 463)
        self.zipFilePath = QtGui.QLineEdit(QAptOfflineInstall)
        self.zipFilePath.setGeometry(QtCore.QRect(30, 60, 270, 30))
        self.zipFilePath.setObjectName("zipFilePath")
        self.browseFilePathButton = QtGui.QPushButton(QAptOfflineInstall)
        self.browseFilePathButton.setGeometry(QtCore.QRect(320, 60, 110, 30))
        self.browseFilePathButton.setObjectName("browseFilePathButton")
        self.startInstallButton = QtGui.QPushButton(QAptOfflineInstall)
        self.startInstallButton.setEnabled(False)
        self.startInstallButton.setGeometry(QtCore.QRect(90, 110, 130, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/dialog-ok-apply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.startInstallButton.setIcon(icon)
        self.startInstallButton.setObjectName("startInstallButton")
        self.cancelButton = QtGui.QPushButton(QAptOfflineInstall)
        self.cancelButton.setGeometry(QtCore.QRect(240, 110, 140, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")
        self.statusProgressBar = QtGui.QProgressBar(QAptOfflineInstall)
        self.statusProgressBar.setGeometry(QtCore.QRect(30, 190, 410, 20))
        self.statusProgressBar.setProperty("value", QtCore.QVariant(0))
        self.statusProgressBar.setObjectName("statusProgressBar")
        self.rawLogHolder = QtGui.QPlainTextEdit(QAptOfflineInstall)
        self.rawLogHolder.setGeometry(QtCore.QRect(30, 230, 410, 210))
        self.rawLogHolder.setObjectName("rawLogHolder")
        self.label = QtGui.QLabel(QAptOfflineInstall)
        self.label.setGeometry(QtCore.QRect(30, 30, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(QAptOfflineInstall)
        self.label_2.setGeometry(QtCore.QRect(40, 170, 70, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.progressStatusDescription = QtGui.QLabel(QAptOfflineInstall)
        self.progressStatusDescription.setGeometry(QtCore.QRect(90, 170, 53, 15))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressStatusDescription.setFont(font)
        self.progressStatusDescription.setObjectName("progressStatusDescription")

        self.retranslateUi(QAptOfflineInstall)
        QtCore.QMetaObject.connectSlotsByName(QAptOfflineInstall)

    def retranslateUi(self, QAptOfflineInstall):
        QAptOfflineInstall.setWindowTitle(QtGui.QApplication.translate("QAptOfflineInstall", "Install Packages", None, QtGui.QApplication.UnicodeUTF8))
        self.browseFilePathButton.setText(QtGui.QApplication.translate("QAptOfflineInstall", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.startInstallButton.setText(QtGui.QApplication.translate("QAptOfflineInstall", "Install", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("QAptOfflineInstall", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("QAptOfflineInstall", "Select the zip file", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("QAptOfflineInstall", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.progressStatusDescription.setText(QtGui.QApplication.translate("QAptOfflineInstall", "Ready", None, QtGui.QApplication.UnicodeUTF8))

