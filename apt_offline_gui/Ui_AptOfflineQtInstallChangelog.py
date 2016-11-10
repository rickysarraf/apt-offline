# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtInstallChangelog.ui'
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

class Ui_AptOfflineQtInstallChangelog(object):
    def setupUi(self, AptOfflineQtInstallChangelog):
        AptOfflineQtInstallChangelog.setObjectName(_fromUtf8("AptOfflineQtInstallChangelog"))
        AptOfflineQtInstallChangelog.resize(670, 675)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineQtInstallChangelog.sizePolicy().hasHeightForWidth())
        AptOfflineQtInstallChangelog.setSizePolicy(sizePolicy)
        AptOfflineQtInstallChangelog.setModal(True)
        self.closeButton = QtGui.QPushButton(AptOfflineQtInstallChangelog)
        self.closeButton.setGeometry(QtCore.QRect(540, 620, 100, 28))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/application-exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.changelogPlainTextEdit = QtGui.QPlainTextEdit(AptOfflineQtInstallChangelog)
        self.changelogPlainTextEdit.setGeometry(QtCore.QRect(20, 50, 621, 561))
        self.changelogPlainTextEdit.setTabChangesFocus(True)
        self.changelogPlainTextEdit.setUndoRedoEnabled(False)
        self.changelogPlainTextEdit.setReadOnly(True)
        self.changelogPlainTextEdit.setObjectName(_fromUtf8("changelogPlainTextEdit"))
        self.label = QtGui.QLabel(AptOfflineQtInstallChangelog)
        self.label.setGeometry(QtCore.QRect(20, 20, 81, 20))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(AptOfflineQtInstallChangelog)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtInstallChangelog)

    def retranslateUi(self, AptOfflineQtInstallChangelog):
        AptOfflineQtInstallChangelog.setWindowTitle(_translate("AptOfflineQtInstallChangelog", "Dialog", None))
        self.closeButton.setToolTip(_translate("AptOfflineQtInstallChangelog", "Close this window", None))
        self.closeButton.setText(_translate("AptOfflineQtInstallChangelog", "Close", None))
        self.label.setText(_translate("AptOfflineQtInstallChangelog", "Changelog", None))

import resources_rc
