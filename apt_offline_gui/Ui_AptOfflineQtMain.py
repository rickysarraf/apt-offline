# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtMain.ui'
#
# Created: Sat Sep 13 15:09:28 2014
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

class Ui_AptOfflineMain(object):
    def setupUi(self, AptOfflineMain):
        AptOfflineMain.setObjectName(_fromUtf8("AptOfflineMain"))
        AptOfflineMain.resize(432, 544)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AptOfflineMain.sizePolicy().hasHeightForWidth())
        AptOfflineMain.setSizePolicy(sizePolicy)
        AptOfflineMain.setMinimumSize(QtCore.QSize(432, 544))
        AptOfflineMain.setMaximumSize(QtCore.QSize(432, 544))
        AptOfflineMain.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        AptOfflineMain.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtGui.QWidget(AptOfflineMain)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.createProfileButton = QtGui.QPushButton(self.centralwidget)
        self.createProfileButton.setGeometry(QtCore.QRect(30, 20, 371, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.createProfileButton.setFont(font)
        self.createProfileButton.setMouseTracking(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/contact-new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.createProfileButton.setIcon(icon)
        self.createProfileButton.setObjectName(_fromUtf8("createProfileButton"))
        self.downloadButton = QtGui.QPushButton(self.centralwidget)
        self.downloadButton.setGeometry(QtCore.QRect(30, 80, 371, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.downloadButton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/go-down.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.downloadButton.setIcon(icon1)
        self.downloadButton.setObjectName(_fromUtf8("downloadButton"))
        self.restoreButton = QtGui.QPushButton(self.centralwidget)
        self.restoreButton.setGeometry(QtCore.QRect(30, 140, 371, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.restoreButton.setFont(font)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/install.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.restoreButton.setIcon(icon2)
        self.restoreButton.setObjectName(_fromUtf8("restoreButton"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(30, 220, 371, 211))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.frame.setFont(font)
        self.frame.setFrameShape(QtGui.QFrame.Box)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.descriptionField = QtGui.QLabel(self.frame)
        self.descriptionField.setGeometry(QtCore.QRect(0, 0, 371, 211))
        self.descriptionField.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.descriptionField.setWordWrap(True)
        self.descriptionField.setMargin(10)
        self.descriptionField.setObjectName(_fromUtf8("descriptionField"))
        self.exitButton = QtGui.QPushButton(self.centralwidget)
        self.exitButton.setGeometry(QtCore.QRect(280, 450, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.exitButton.setFont(font)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/application-exit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitButton.setIcon(icon3)
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 200, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        AptOfflineMain.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(AptOfflineMain)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        AptOfflineMain.setStatusBar(self.statusbar)
        self.menubar = QtGui.QMenuBar(AptOfflineMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 432, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuOperations = QtGui.QMenu(self.menubar)
        self.menuOperations.setObjectName(_fromUtf8("menuOperations"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        AptOfflineMain.setMenuBar(self.menubar)
        self.menuCreateProfile = QtGui.QAction(AptOfflineMain)
        self.menuCreateProfile.setIcon(icon)
        self.menuCreateProfile.setObjectName(_fromUtf8("menuCreateProfile"))
        self.menuDownload = QtGui.QAction(AptOfflineMain)
        self.menuDownload.setIcon(icon1)
        self.menuDownload.setObjectName(_fromUtf8("menuDownload"))
        self.menuInstall = QtGui.QAction(AptOfflineMain)
        self.menuInstall.setIcon(icon2)
        self.menuInstall.setObjectName(_fromUtf8("menuInstall"))
        self.menuExit = QtGui.QAction(AptOfflineMain)
        self.menuExit.setIcon(icon3)
        self.menuExit.setObjectName(_fromUtf8("menuExit"))
        self.menuHelp_2 = QtGui.QAction(AptOfflineMain)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/help-contents.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuHelp_2.setIcon(icon4)
        self.menuHelp_2.setObjectName(_fromUtf8("menuHelp_2"))
        self.menuAbout = QtGui.QAction(AptOfflineMain)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/help-about.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuAbout.setIcon(icon5)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
        self.menuOperations.addAction(self.menuCreateProfile)
        self.menuOperations.addAction(self.menuDownload)
        self.menuOperations.addAction(self.menuInstall)
        self.menuOperations.addSeparator()
        self.menuOperations.addAction(self.menuExit)
        self.menuHelp.addAction(self.menuHelp_2)
        self.menuHelp.addAction(self.menuAbout)
        self.menubar.addAction(self.menuOperations.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(AptOfflineMain)
        QtCore.QMetaObject.connectSlotsByName(AptOfflineMain)

    def retranslateUi(self, AptOfflineMain):
        AptOfflineMain.setWindowTitle(_translate("AptOfflineMain", "APT Offline", None))
        self.createProfileButton.setText(_translate("AptOfflineMain", "Generate Signature", None))
        self.downloadButton.setText(_translate("AptOfflineMain", "Download Packages or Updates", None))
        self.restoreButton.setText(_translate("AptOfflineMain", "Install Packages or Updates", None))
        self.descriptionField.setText(_translate("AptOfflineMain", "Hover your mouse over the buttons to get the description", None))
        self.exitButton.setText(_translate("AptOfflineMain", "Exit", None))
        self.label_2.setText(_translate("AptOfflineMain", "Description", None))
        self.menuOperations.setTitle(_translate("AptOfflineMain", "Operations", None))
        self.menuHelp.setTitle(_translate("AptOfflineMain", "Help", None))
        self.menuCreateProfile.setText(_translate("AptOfflineMain", "Generate Signature", None))
        self.menuCreateProfile.setShortcut(_translate("AptOfflineMain", "Ctrl+N", None))
        self.menuDownload.setText(_translate("AptOfflineMain", "Download Packages or Updates", None))
        self.menuDownload.setShortcut(_translate("AptOfflineMain", "Ctrl+O", None))
        self.menuInstall.setText(_translate("AptOfflineMain", "Install Packages or Updates", None))
        self.menuInstall.setShortcut(_translate("AptOfflineMain", "Ctrl+I", None))
        self.menuExit.setText(_translate("AptOfflineMain", "Exit", None))
        self.menuExit.setShortcut(_translate("AptOfflineMain", "Ctrl+Q", None))
        self.menuHelp_2.setText(_translate("AptOfflineMain", "Help", None))
        self.menuHelp_2.setShortcut(_translate("AptOfflineMain", "F1", None))
        self.menuAbout.setText(_translate("AptOfflineMain", "About apt-offline", None))

import resources_rc
