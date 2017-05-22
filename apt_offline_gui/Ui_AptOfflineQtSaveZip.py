# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtSaveZip.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SaveZipFile(object):
    def setupUi(self, SaveZipFile):
        SaveZipFile.setObjectName("SaveZipFile")
        SaveZipFile.setWindowModality(QtCore.Qt.WindowModal)
        SaveZipFile.resize(445, 176)
        self.zipFilePath = QtWidgets.QLineEdit(SaveZipFile)
        self.zipFilePath.setGeometry(QtCore.QRect(20, 70, 291, 31))
        self.zipFilePath.setObjectName("zipFilePath")
        self.label = QtWidgets.QLabel(SaveZipFile)
        self.label.setGeometry(QtCore.QRect(20, 0, 401, 71))
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.browseFilePathButton = QtWidgets.QPushButton(SaveZipFile)
        self.browseFilePathButton.setGeometry(QtCore.QRect(330, 70, 101, 31))
        self.browseFilePathButton.setObjectName("browseFilePathButton")
        self.saveButton = QtWidgets.QPushButton(SaveZipFile)
        self.saveButton.setGeometry(QtCore.QRect(90, 120, 121, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/document-save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon)
        self.saveButton.setObjectName("saveButton")
        self.cancelButton = QtWidgets.QPushButton(SaveZipFile)
        self.cancelButton.setGeometry(QtCore.QRect(240, 120, 121, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/dialog-cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName("cancelButton")

        self.retranslateUi(SaveZipFile)
        QtCore.QMetaObject.connectSlotsByName(SaveZipFile)

    def retranslateUi(self, SaveZipFile):
        _translate = QtCore.QCoreApplication.translate
        SaveZipFile.setWindowTitle(_translate("SaveZipFile", "Packages downloaded successfully"))
        self.label.setText(_translate("SaveZipFile", "Success! The packages have been downloaded. Please specify the location where you want the zip file of the packages to be saved"))
        self.browseFilePathButton.setText(_translate("SaveZipFile", "Browse"))
        self.saveButton.setText(_translate("SaveZipFile", "Save"))
        self.cancelButton.setText(_translate("SaveZipFile", "Cancel"))

import resources_rc
