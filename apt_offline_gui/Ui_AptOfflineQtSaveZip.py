# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtSaveZip.ui'
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

class Ui_SaveZipFile(object):
    def setupUi(self, SaveZipFile):
        SaveZipFile.setObjectName(_fromUtf8("SaveZipFile"))
        SaveZipFile.setWindowModality(QtCore.Qt.WindowModal)
        SaveZipFile.resize(445, 176)
        self.zipFilePath = QtGui.QLineEdit(SaveZipFile)
        self.zipFilePath.setGeometry(QtCore.QRect(20, 70, 291, 31))
        self.zipFilePath.setObjectName(_fromUtf8("zipFilePath"))
        self.label = QtGui.QLabel(SaveZipFile)
        self.label.setGeometry(QtCore.QRect(20, 0, 401, 71))
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.browseFilePathButton = QtGui.QPushButton(SaveZipFile)
        self.browseFilePathButton.setGeometry(QtCore.QRect(330, 70, 101, 31))
        self.browseFilePathButton.setObjectName(_fromUtf8("browseFilePathButton"))
        self.saveButton = QtGui.QPushButton(SaveZipFile)
        self.saveButton.setGeometry(QtCore.QRect(90, 120, 121, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/document-save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.cancelButton = QtGui.QPushButton(SaveZipFile)
        self.cancelButton.setGeometry(QtCore.QRect(240, 120, 121, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/dialog-cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon1)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))

        self.retranslateUi(SaveZipFile)
        QtCore.QMetaObject.connectSlotsByName(SaveZipFile)

    def retranslateUi(self, SaveZipFile):
        SaveZipFile.setWindowTitle(_translate("SaveZipFile", "Packages downloaded successfully", None))
        self.label.setText(_translate("SaveZipFile", "Success! The packages have been downloaded. Please specify the location where you want the zip file of the packages to be saved", None))
        self.browseFilePathButton.setText(_translate("SaveZipFile", "Browse", None))
        self.saveButton.setText(_translate("SaveZipFile", "Save", None))
        self.cancelButton.setText(_translate("SaveZipFile", "Cancel", None))

import resources_rc
