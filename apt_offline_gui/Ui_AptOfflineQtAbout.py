# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AptOfflineQtAbout.ui'
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

class Ui_AboutAptOffline(object):
    def setupUi(self, AboutAptOffline):
        AboutAptOffline.setObjectName(_fromUtf8("AboutAptOffline"))
        AboutAptOffline.setWindowModality(QtCore.Qt.ApplicationModal)
        AboutAptOffline.resize(526, 378)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutAptOffline.sizePolicy().hasHeightForWidth())
        AboutAptOffline.setSizePolicy(sizePolicy)
        AboutAptOffline.setMinimumSize(QtCore.QSize(526, 378))
        AboutAptOffline.setMaximumSize(QtCore.QSize(526, 378))
        self.label = QtGui.QLabel(AboutAptOffline)
        self.label.setGeometry(QtCore.QRect(12, 30, 511, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.tabWidget = QtGui.QTabWidget(AboutAptOffline)
        self.tabWidget.setGeometry(QtCore.QRect(7, 90, 510, 241))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.aboutTab = QtGui.QWidget()
        self.aboutTab.setObjectName(_fromUtf8("aboutTab"))
        self.label_3 = QtGui.QLabel(self.aboutTab)
        self.label_3.setGeometry(QtCore.QRect(10, 20, 491, 31))
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_14 = QtGui.QLabel(self.aboutTab)
        self.label_14.setGeometry(QtCore.QRect(10, 60, 481, 111))
        self.label_14.setScaledContents(True)
        self.label_14.setWordWrap(True)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.tabWidget.addTab(self.aboutTab, _fromUtf8(""))
        self.authorTab = QtGui.QWidget()
        self.authorTab.setObjectName(_fromUtf8("authorTab"))
        self.label_4 = QtGui.QLabel(self.authorTab)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.authorTab)
        self.label_5.setGeometry(QtCore.QRect(30, 30, 271, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(self.authorTab)
        self.label_6.setGeometry(QtCore.QRect(10, 60, 131, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(self.authorTab)
        self.label_7.setGeometry(QtCore.QRect(30, 80, 261, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(self.authorTab)
        self.label_8.setGeometry(QtCore.QRect(30, 100, 271, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.tabWidget.addTab(self.authorTab, _fromUtf8(""))
        self.thanksTab = QtGui.QWidget()
        self.thanksTab.setObjectName(_fromUtf8("thanksTab"))
        self.label_9 = QtGui.QLabel(self.thanksTab)
        self.label_9.setGeometry(QtCore.QRect(10, 10, 221, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(self.thanksTab)
        self.label_10.setGeometry(QtCore.QRect(10, 30, 141, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(self.thanksTab)
        self.label_11.setGeometry(QtCore.QRect(10, 50, 161, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_12 = QtGui.QLabel(self.thanksTab)
        self.label_12.setGeometry(QtCore.QRect(10, 70, 161, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.label_13 = QtGui.QLabel(self.thanksTab)
        self.label_13.setGeometry(QtCore.QRect(10, 110, 471, 51))
        self.label_13.setScaledContents(True)
        self.label_13.setWordWrap(True)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.tabWidget.addTab(self.thanksTab, _fromUtf8(""))
        self.licenseTab = QtGui.QWidget()
        self.licenseTab.setObjectName(_fromUtf8("licenseTab"))
        self.licenseText = QtGui.QPlainTextEdit(self.licenseTab)
        self.licenseText.setGeometry(QtCore.QRect(4, 4, 490, 203))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.licenseText.setFont(font)
        self.licenseText.setAcceptDrops(False)
        self.licenseText.setUndoRedoEnabled(False)
        self.licenseText.setReadOnly(True)
        self.licenseText.setObjectName(_fromUtf8("licenseText"))
        self.tabWidget.addTab(self.licenseTab, _fromUtf8(""))
        self.label_2 = QtGui.QLabel(AboutAptOffline)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 511, 16))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.pushButton = QtGui.QPushButton(AboutAptOffline)
        self.pushButton.setGeometry(QtCore.QRect(416, 340, 101, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/dialog-cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))

        self.retranslateUi(AboutAptOffline)
        self.tabWidget.setCurrentIndex(3)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), AboutAptOffline.close)
        QtCore.QMetaObject.connectSlotsByName(AboutAptOffline)
        AboutAptOffline.setTabOrder(self.tabWidget, self.licenseText)
        AboutAptOffline.setTabOrder(self.licenseText, self.pushButton)

    def retranslateUi(self, AboutAptOffline):
        AboutAptOffline.setWindowTitle(_translate("AboutAptOffline", "About Apt-Offline", None))
        self.label.setText(_translate("AboutAptOffline", "Apt-Offline", None))
        self.label_3.setText(_translate("AboutAptOffline", "apt-offline is an Offline APT Package Manager for Debian and derivatives. ", None))
        self.label_14.setText(_translate("AboutAptOffline", "apt-offline can fully update/upgrade your disconnected Debian box without the need of connecting it to the network.  \n"
"\n"
"This is a Graphical User Interface which exposes the functionality of apt-offline.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.aboutTab), _translate("AboutAptOffline", "About", None))
        self.label_4.setText(_translate("AboutAptOffline", "Written by:", None))
        self.label_5.setText(_translate("AboutAptOffline", "Ritesh Raj Sarraf <rrs@researchut.com>", None))
        self.label_6.setText(_translate("AboutAptOffline", "GUI written by:", None))
        self.label_7.setText(_translate("AboutAptOffline", "Manish Sinha <mail@manishsinha.net>", None))
        self.label_8.setText(_translate("AboutAptOffline", "Abhishek Mishra <ideamonk@gmail.com>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.authorTab), _translate("AboutAptOffline", "Author", None))
        self.label_9.setText(_translate("AboutAptOffline", "Peter Otten", None))
        self.label_10.setText(_translate("AboutAptOffline", "Duncan Booth", None))
        self.label_11.setText(_translate("AboutAptOffline", "Simon Forman", None))
        self.label_12.setText(_translate("AboutAptOffline", "Dennis Lee Bieber", None))
        self.label_13.setText(_translate("AboutAptOffline", "The awesome Directi people for their office space required for the mini hackfests", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.thanksTab), _translate("AboutAptOffline", "Thanks To", None))
        self.licenseText.setPlainText(_translate("AboutAptOffline", "                    GNU GENERAL PUBLIC LICENSE\n"
"                       Version 3, 29 June 2007\n"
"\n"
" Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>\n"
" Everyone is permitted to copy and distribute verbatim copies\n"
" of this license document, but changing it is not allowed.\n"
"\n"
"\n"
"apt-offline is Copyright (C) - Ritesh Raj Sarraf", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.licenseTab), _translate("AboutAptOffline", "License", None))
        self.label_2.setText(_translate("AboutAptOffline", "A GUI for apt-offline - an offline APT Package Manager", None))
        self.pushButton.setText(_translate("AboutAptOffline", "Close", None))

import resources_rc
