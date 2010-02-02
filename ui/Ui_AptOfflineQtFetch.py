# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtFetch.ui'
#
# Created: Tue Feb  2 23:59:26 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_QAptOfflineFetch(object):
    def setupUi(self, QAptOfflineFetch):
        QAptOfflineFetch.setObjectName("QAptOfflineFetch")
        QAptOfflineFetch.setWindowModality(QtCore.Qt.WindowModal)
        QAptOfflineFetch.resize(466, 463)
        self.profileFilePath = QtGui.QLineEdit(QAptOfflineFetch)
        self.profileFilePath.setGeometry(QtCore.QRect(30, 60, 270, 30))
        self.profileFilePath.setObjectName("profileFilePath")
        self.browseFilePathButton = QtGui.QPushButton(QAptOfflineFetch)
        self.browseFilePathButton.setGeometry(QtCore.QRect(320, 60, 110, 30))
        self.browseFilePathButton.setObjectName("browseFilePathButton")
        self.startDownloadButton = QtGui.QPushButton(QAptOfflineFetch)
        self.startDownloadButton.setEnabled(False)
        self.startDownloadButton.setGeometry(QtCore.QRect(90, 110, 130, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Active, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Disabled, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap("icons/go-down.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.startDownloadButton.setIcon(icon)
        self.startDownloadButton.setCheckable(False)
        self.startDownloadButton.setChecked(False)
        self.startDownloadButton.setFlat(False)
        self.startDownloadButton.setObjectName("startDownloadButton")
        self.cancelButton = QtGui.QPushButton(QAptOfflineFetch)
        self.cancelButton.setGeometry(QtCore.QRect(240, 110, 140, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")
        self.label = QtGui.QLabel(QAptOfflineFetch)
        self.label.setGeometry(QtCore.QRect(30, 30, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.statusProgressBar = QtGui.QProgressBar(QAptOfflineFetch)
        self.statusProgressBar.setGeometry(QtCore.QRect(30, 190, 410, 20))
        self.statusProgressBar.setProperty("value", QtCore.QVariant(0))
        self.statusProgressBar.setObjectName("statusProgressBar")
        self.rawLogHolder = QtGui.QPlainTextEdit(QAptOfflineFetch)
        self.rawLogHolder.setGeometry(QtCore.QRect(30, 230, 410, 210))
        self.rawLogHolder.setObjectName("rawLogHolder")
        self.label_2 = QtGui.QLabel(QAptOfflineFetch)
        self.label_2.setGeometry(QtCore.QRect(40, 170, 70, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.progressStatusDescription = QtGui.QLabel(QAptOfflineFetch)
        self.progressStatusDescription.setGeometry(QtCore.QRect(90, 170, 53, 15))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressStatusDescription.setFont(font)
        self.progressStatusDescription.setObjectName("progressStatusDescription")

        self.retranslateUi(QAptOfflineFetch)
        QtCore.QMetaObject.connectSlotsByName(QAptOfflineFetch)

    def retranslateUi(self, QAptOfflineFetch):
        QAptOfflineFetch.setWindowTitle(QtGui.QApplication.translate("QAptOfflineFetch", "Fetch Packages or Upgrade", None, QtGui.QApplication.UnicodeUTF8))
        self.browseFilePathButton.setText(QtGui.QApplication.translate("QAptOfflineFetch", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.startDownloadButton.setText(QtGui.QApplication.translate("QAptOfflineFetch", "Download", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("QAptOfflineFetch", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("QAptOfflineFetch", "Select the profile file", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("QAptOfflineFetch", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.progressStatusDescription.setText(QtGui.QApplication.translate("QAptOfflineFetch", "Ready", None, QtGui.QApplication.UnicodeUTF8))

