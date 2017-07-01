# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtInstallChangelog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AptOfflineQtInstallChangelog(object):
    def setupUi(self, AptOfflineQtInstallChangelog):
        AptOfflineQtInstallChangelog.setObjectName("AptOfflineQtInstallChangelog")
        AptOfflineQtInstallChangelog.resize(670, 675)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineQtInstallChangelog.sizePolicy().hasHeightForWidth())
        AptOfflineQtInstallChangelog.setSizePolicy(sizePolicy)
        AptOfflineQtInstallChangelog.setModal(True)
        self.closeButton = QtWidgets.QPushButton(AptOfflineQtInstallChangelog)
        self.closeButton.setGeometry(QtCore.QRect(540, 620, 100, 28))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/application-exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon)
        self.closeButton.setObjectName("closeButton")
        self.changelogPlainTextEdit = QtWidgets.QPlainTextEdit(AptOfflineQtInstallChangelog)
        self.changelogPlainTextEdit.setGeometry(QtCore.QRect(20, 50, 621, 561))
        self.changelogPlainTextEdit.setTabChangesFocus(True)
        self.changelogPlainTextEdit.setUndoRedoEnabled(False)
        self.changelogPlainTextEdit.setReadOnly(True)
        self.changelogPlainTextEdit.setObjectName("changelogPlainTextEdit")
        self.label = QtWidgets.QLabel(AptOfflineQtInstallChangelog)
        self.label.setGeometry(QtCore.QRect(20, 20, 81, 20))
        self.label.setObjectName("label")

        self.retranslateUi(AptOfflineQtInstallChangelog)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtInstallChangelog)

    def retranslateUi(self, AptOfflineQtInstallChangelog):
        _translate = QtCore.QCoreApplication.translate
        AptOfflineQtInstallChangelog.setWindowTitle(_translate("AptOfflineQtInstallChangelog", "Dialog"))
        self.closeButton.setToolTip(_translate("AptOfflineQtInstallChangelog", "Close this window"))
        self.closeButton.setText(_translate("AptOfflineQtInstallChangelog", "Close"))
        self.label.setText(_translate("AptOfflineQtInstallChangelog", "Changelog"))

from . import resources_rc
