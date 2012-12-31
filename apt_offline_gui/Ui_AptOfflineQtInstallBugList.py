# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtInstallBugList.ui'
#
# Created: Mon Dec 31 15:13:48 2012
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AptOfflineQtInstallBugList(object):
    def setupUi(self, AptOfflineQtInstallBugList):
        AptOfflineQtInstallBugList.setObjectName(_fromUtf8("AptOfflineQtInstallBugList"))
        AptOfflineQtInstallBugList.resize(642, 674)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineQtInstallBugList.sizePolicy().hasHeightForWidth())
        AptOfflineQtInstallBugList.setSizePolicy(sizePolicy)
        AptOfflineQtInstallBugList.setModal(True)
        self.bugListViewWindow = QtGui.QListWidget(AptOfflineQtInstallBugList)
        self.bugListViewWindow.setGeometry(QtCore.QRect(30, 40, 581, 81))
        self.bugListViewWindow.setObjectName(_fromUtf8("bugListViewWindow"))
        self.closeButton = QtGui.QPushButton(AptOfflineQtInstallBugList)
        self.closeButton.setGeometry(QtCore.QRect(500, 630, 107, 24))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/application-exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.label = QtGui.QLabel(AptOfflineQtInstallBugList)
        self.label.setGeometry(QtCore.QRect(30, 10, 231, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.bugListplainTextEdit = QtGui.QPlainTextEdit(AptOfflineQtInstallBugList)
        self.bugListplainTextEdit.setGeometry(QtCore.QRect(30, 160, 581, 441))
        self.bugListplainTextEdit.setAcceptDrops(False)
        self.bugListplainTextEdit.setReadOnly(True)
        self.bugListplainTextEdit.setObjectName(_fromUtf8("bugListplainTextEdit"))

        self.retranslateUi(AptOfflineQtInstallBugList)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtInstallBugList)

    def retranslateUi(self, AptOfflineQtInstallBugList):
        AptOfflineQtInstallBugList.setWindowTitle(QtGui.QApplication.translate("AptOfflineQtInstallBugList", "List of Bugs", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setToolTip(QtGui.QApplication.translate("AptOfflineQtInstallBugList", "<html><head/><body><p>Close this window</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("AptOfflineQtInstallBugList", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AptOfflineQtInstallBugList", "List of bugs", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
