# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtSaveZip.ui'
#
# Created: Tue Feb  2 23:58:56 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SaveZipFile(object):
    def setupUi(self, SaveZipFile):
        SaveZipFile.setObjectName("SaveZipFile")
        SaveZipFile.setWindowModality(QtCore.Qt.WindowModal)
        SaveZipFile.resize(445, 176)
        self.zipFilePath = QtGui.QLineEdit(SaveZipFile)
        self.zipFilePath.setGeometry(QtCore.QRect(20, 70, 291, 31))
        self.zipFilePath.setObjectName("zipFilePath")
        self.label = QtGui.QLabel(SaveZipFile)
        self.label.setGeometry(QtCore.QRect(20, 0, 401, 71))
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.browseFilePathButton = QtGui.QPushButton(SaveZipFile)
        self.browseFilePathButton.setGeometry(QtCore.QRect(330, 70, 101, 31))
        self.browseFilePathButton.setObjectName("browseFilePathButton")
        self.saveButton = QtGui.QPushButton(SaveZipFile)
        self.saveButton.setGeometry(QtCore.QRect(90, 120, 121, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/document-save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon)
        self.saveButton.setObjectName("saveButton")
        self.cancelButton = QtGui.QPushButton(SaveZipFile)
        self.cancelButton.setGeometry(QtCore.QRect(240, 120, 121, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")

        self.retranslateUi(SaveZipFile)
        QtCore.QMetaObject.connectSlotsByName(SaveZipFile)

    def retranslateUi(self, SaveZipFile):
        SaveZipFile.setWindowTitle(QtGui.QApplication.translate("SaveZipFile", "Packages downloaded successfully", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SaveZipFile", "Success! The packages have been downloaded. Please specify the location where you want the zip file of the packages to be saved", None, QtGui.QApplication.UnicodeUTF8))
        self.browseFilePathButton.setText(QtGui.QApplication.translate("SaveZipFile", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.saveButton.setText(QtGui.QApplication.translate("SaveZipFile", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("SaveZipFile", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

