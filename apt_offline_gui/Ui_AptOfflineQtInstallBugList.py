# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtInstallBugList.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AptOfflineQtInstallBugList(object):
    def setupUi(self, AptOfflineQtInstallBugList):
        AptOfflineQtInstallBugList.setObjectName("AptOfflineQtInstallBugList")
        AptOfflineQtInstallBugList.resize(642, 674)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineQtInstallBugList.sizePolicy().hasHeightForWidth())
        AptOfflineQtInstallBugList.setSizePolicy(sizePolicy)
        AptOfflineQtInstallBugList.setMinimumSize(QtCore.QSize(642, 674))
        AptOfflineQtInstallBugList.setMaximumSize(QtCore.QSize(642, 674))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/help-about.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AptOfflineQtInstallBugList.setWindowIcon(icon)
        AptOfflineQtInstallBugList.setModal(True)
        self.bugListViewWindow = QtWidgets.QListWidget(AptOfflineQtInstallBugList)
        self.bugListViewWindow.setGeometry(QtCore.QRect(30, 30, 581, 121))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.bugListViewWindow.setFont(font)
        self.bugListViewWindow.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.bugListViewWindow.setTabKeyNavigation(False)
        self.bugListViewWindow.setResizeMode(QtWidgets.QListView.Adjust)
        self.bugListViewWindow.setObjectName("bugListViewWindow")
        self.label = QtWidgets.QLabel(AptOfflineQtInstallBugList)
        self.label.setGeometry(QtCore.QRect(30, 10, 231, 16))
        self.label.setObjectName("label")
        self.bugListplainTextEdit = QtWidgets.QPlainTextEdit(AptOfflineQtInstallBugList)
        self.bugListplainTextEdit.setGeometry(QtCore.QRect(30, 170, 581, 461))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.bugListplainTextEdit.setFont(font)
        self.bugListplainTextEdit.setAcceptDrops(False)
        self.bugListplainTextEdit.setFrameShape(QtWidgets.QFrame.Panel)
        self.bugListplainTextEdit.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.bugListplainTextEdit.setTabChangesFocus(True)
        self.bugListplainTextEdit.setUndoRedoEnabled(False)
        self.bugListplainTextEdit.setReadOnly(True)
        self.bugListplainTextEdit.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.bugListplainTextEdit.setObjectName("bugListplainTextEdit")
        self.closeButton = QtWidgets.QPushButton(AptOfflineQtInstallBugList)
        self.closeButton.setGeometry(QtCore.QRect(510, 640, 100, 28))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/application-exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon1)
        self.closeButton.setObjectName("closeButton")

        self.retranslateUi(AptOfflineQtInstallBugList)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineQtInstallBugList)

    def retranslateUi(self, AptOfflineQtInstallBugList):
        _translate = QtCore.QCoreApplication.translate
        AptOfflineQtInstallBugList.setWindowTitle(_translate("AptOfflineQtInstallBugList", "List of Bugs"))
        self.bugListViewWindow.setToolTip(_translate("AptOfflineQtInstallBugList", "Bug List"))
        self.bugListViewWindow.setStatusTip(_translate("AptOfflineQtInstallBugList", "Bug List"))
        self.bugListViewWindow.setWhatsThis(_translate("AptOfflineQtInstallBugList", "Bug List"))
        self.bugListViewWindow.setSortingEnabled(True)
        self.label.setText(_translate("AptOfflineQtInstallBugList", "List of bugs"))
        self.bugListplainTextEdit.setToolTip(_translate("AptOfflineQtInstallBugList", "Bug Report Content"))
        self.bugListplainTextEdit.setStatusTip(_translate("AptOfflineQtInstallBugList", "Bug Report Content"))
        self.bugListplainTextEdit.setWhatsThis(_translate("AptOfflineQtInstallBugList", "Bug Report Content"))
        self.closeButton.setToolTip(_translate("AptOfflineQtInstallBugList", "Close this window"))
        self.closeButton.setText(_translate("AptOfflineQtInstallBugList", "Close"))

from . import resources_rc
