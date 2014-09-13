# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtInstallBugList.ui'
#
# Created: Sat Sep 13 15:09:29 2014
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_AptOfflineQtInstallBugList(object):
    def setupUi(self, AptOfflineQtInstallBugList):
        AptOfflineQtInstallBugList.setObjectName(_fromUtf8("AptOfflineQtInstallBugList"))
        AptOfflineQtInstallBugList.resize(642, 674)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineQtInstallBugList.sizePolicy().hasHeightForWidth())
        AptOfflineQtInstallBugList.setSizePolicy(sizePolicy)
        AptOfflineQtInstallBugList.setMinimumSize(QtCore.QSize(642, 674))
        AptOfflineQtInstallBugList.setMaximumSize(QtCore.QSize(642, 674))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/help-about.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AptOfflineQtInstallBugList.setWindowIcon(icon)
        AptOfflineQtInstallBugList.setModal(True)
        self.bugListViewWindow = QtGui.QListWidget(AptOfflineQtInstallBugList)
        self.bugListViewWindow.setGeometry(QtCore.QRect(30, 30, 581, 121))
        self.bugListViewWindow.setFrameShape(QtGui.QFrame.WinPanel)
        self.bugListViewWindow.setTabKeyNavigation(False)
        self.bugListViewWindow.setResizeMode(QtGui.QListView.Adjust)
        self.bugListViewWindow.setObjectName(_fromUtf8("bugListViewWindow"))
        self.label = QtGui.QLabel(AptOfflineQtInstallBugList)
        self.label.setGeometry(QtCore.QRect(30, 10, 231, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.bugListplainTextEdit = QtGui.QPlainTextEdit(AptOfflineQtInstallBugList)
        self.bugListplainTextEdit.setGeometry(QtCore.QRect(30, 170, 581, 461))
        self.bugListplainTextEdit.setAcceptDrops(False)
        self.bugListplainTextEdit.setFrameShape(QtGui.QFrame.Panel)
        self.bugListplainTextEdit.setFrameShadow(QtGui.QFrame.Sunken)
        self.bugListplainTextEdit.setTabChangesFocus(True)
        self.bugListplainTextEdit.setUndoRedoEnabled(False)
        self.bugListplainTextEdit.setReadOnly(True)
        self.bugListplainTextEdit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.bugListplainTextEdit.setObjectName(_fromUtf8("bugListplainTextEdit"))
        self.closeButton = QtGui.QPushButton(AptOfflineQtInstallBugList)
        self.closeButton.setGeometry(QtCore.QRect(510, 640, 100, 28))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/application-exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon1)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))

        self.retranslateUi(AptOfflineQtInstallBugList)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtInstallBugList)

    def retranslateUi(self, AptOfflineQtInstallBugList):
        AptOfflineQtInstallBugList.setWindowTitle(_translate("AptOfflineQtInstallBugList", "List of Bugs", None))
        self.bugListViewWindow.setToolTip(_translate("AptOfflineQtInstallBugList", "Bug List", None))
        self.bugListViewWindow.setStatusTip(_translate("AptOfflineQtInstallBugList", "Bug List", None))
        self.bugListViewWindow.setWhatsThis(_translate("AptOfflineQtInstallBugList", "Bug List", None))
        self.bugListViewWindow.setSortingEnabled(True)
        self.label.setText(_translate("AptOfflineQtInstallBugList", "List of bugs", None))
        self.bugListplainTextEdit.setToolTip(_translate("AptOfflineQtInstallBugList", "Bug Report Content", None))
        self.bugListplainTextEdit.setStatusTip(_translate("AptOfflineQtInstallBugList", "Bug Report Content", None))
        self.bugListplainTextEdit.setWhatsThis(_translate("AptOfflineQtInstallBugList", "Bug Report Content", None))
        self.closeButton.setToolTip(_translate("AptOfflineQtInstallBugList", "Close this window", None))
        self.closeButton.setText(_translate("AptOfflineQtInstallBugList", "Close", None))

import resources_rc
