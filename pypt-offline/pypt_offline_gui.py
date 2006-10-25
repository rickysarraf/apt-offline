# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'temp.ui'
#
# Created: Wed Oct 25 02:13:43 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.16
#
# WARNING! All changes made in this file will be lost!


from qt import *


class Form1(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setName("Form1")


        self.setCentralWidget(QWidget(self,"qt_central_widget"))

        self.pushButton1 = QPushButton(self.centralWidget(),"pushButton1")
        self.pushButton1.setGeometry(QRect(490,390,91,31))

        self.textLabel1 = QLabel(self.centralWidget(),"textLabel1")
        self.textLabel1.setGeometry(QRect(15,20,151,21))

        self.textLabel2 = QLabel(self.centralWidget(),"textLabel2")
        self.textLabel2.setGeometry(QRect(210,15,151,31))

        self.comboBox2 = QComboBox(0,self.centralWidget(),"comboBox2")
        self.comboBox2.setEnabled(0)
        self.comboBox2.setGeometry(QRect(210,50,150,31))

        self.comboBox1 = QComboBox(0,self.centralWidget(),"comboBox1")
        self.comboBox1.setGeometry(QRect(10,50,160,31))
        self.comboBox1.setMouseTracking(1)

        self.frame3 = QFrame(self.centralWidget(),"frame3")
        self.frame3.setEnabled(0)
        self.frame3.setGeometry(QRect(10,90,441,311))
        self.frame3.setFrameShape(QFrame.StyledPanel)
        self.frame3.setFrameShadow(QFrame.Raised)

        self.textLabel1_2 = QLabel(self.frame3,"textLabel1_2")
        self.textLabel1_2.setEnabled(0)
        self.textLabel1_2.setGeometry(QRect(30,70,351,71))

        self.pushButton2 = QPushButton(self.frame3,"pushButton2")
        self.pushButton2.setGeometry(QRect(310,226,101,31))

        self.fileExitAction = QAction(self,"fileExitAction")
        self.helpContentsAction = QAction(self,"helpContentsAction")
        self.helpIndexAction = QAction(self,"helpIndexAction")
        self.helpAboutAction = QAction(self,"helpAboutAction")




        self.MenuBar = QMenuBar(self,"MenuBar")


        self.fileMenu = QPopupMenu(self)
        self.fileMenu.insertSeparator()
        self.fileMenu.insertSeparator()
        self.fileExitAction.addTo(self.fileMenu)
        self.MenuBar.insertItem(QString(""),self.fileMenu,1)

        self.helpMenu = QPopupMenu(self)
        self.helpContentsAction.addTo(self.helpMenu)
        self.helpIndexAction.addTo(self.helpMenu)
        self.helpMenu.insertSeparator()
        self.helpAboutAction.addTo(self.helpMenu)
        self.MenuBar.insertItem(QString(""),self.helpMenu,2)


        self.languageChange()

        self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.fileExitAction,SIGNAL("activated()"),self.close)
        self.connect(self.helpIndexAction,SIGNAL("activated()"),self.helpIndex)
        self.connect(self.helpContentsAction,SIGNAL("activated()"),self.helpContents)
        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)
        self.connect(self.comboBox1,SIGNAL("activated(int)"),self.whichOption)
        self.connect(self.comboBox2,SIGNAL("activated(int)"),self.whichUpgradeOption)


    def languageChange(self):
        self.setCaption(self.__tr("pypt-offline"))
        self.pushButton1.setText(self.__tr("Start"))
        self.textLabel1.setText(self.__tr("<p align=\"center\">Options</p>"))
        self.textLabel2.setText(self.__tr("<p align=\"center\">Upgrade Options</p>"))
        self.comboBox2.clear()
        self.comboBox2.insertItem(self.__tr("upgrade"))
        self.comboBox2.insertItem(self.__tr("dist-upgrade"))
        self.comboBox2.insertItem(self.__tr("dselect-upgrade"))
        self.comboBox1.clear()
        self.comboBox1.insertItem(self.__tr("set-update"))
        self.comboBox1.insertItem(self.__tr("set-upgrade"))
        self.comboBox1.insertItem(self.__tr("fetch-update"))
        self.comboBox1.insertItem(self.__tr("fetch-upgrade"))
        self.comboBox1.insertItem(self.__tr("install-update"))
        self.comboBox1.insertItem(self.__tr("install-upgrade"))
        QToolTip.add(self.comboBox1,self.__tr("Select Option"))
        QWhatsThis.add(self.comboBox1,self.__tr("Select the option you want pypt-offline to execute"))
        self.textLabel1_2.setText(self.__tr("pypt-offline user interface. TBD"))
        self.pushButton2.setText(self.__tr("pushButton2"))
        self.fileExitAction.setText(self.__tr("Exit"))
        self.fileExitAction.setMenuText(self.__tr("E&xit"))
        self.fileExitAction.setAccel(QString.null)
        self.helpContentsAction.setText(self.__tr("Contents"))
        self.helpContentsAction.setMenuText(self.__tr("&Contents..."))
        self.helpContentsAction.setAccel(QString.null)
        self.helpIndexAction.setText(self.__tr("Index"))
        self.helpIndexAction.setMenuText(self.__tr("&Index..."))
        self.helpIndexAction.setAccel(QString.null)
        self.helpAboutAction.setText(self.__tr("About"))
        self.helpAboutAction.setMenuText(self.__tr("&About"))
        self.helpAboutAction.setAccel(QString.null)
        if self.MenuBar.findItem(1):
            self.MenuBar.findItem(1).setText(self.__tr("&File"))
        if self.MenuBar.findItem(2):
            self.MenuBar.findItem(2).setText(self.__tr("&Help"))


    def fileExit(self):
        print "Form1.fileExit(): Not implemented yet"

    def helpIndex(self):
        print "Form1.helpIndex(): Not implemented yet"

    def helpContents(self):
        print "Form1.helpContents(): Not implemented yet"

    def helpAbout(self):
        print "Form1.helpAbout(): Not implemented yet"

    def whichOption(self,a0):
        	if self.comboBox1.currentItem() == 0:
        		# set-update
        		pass
        	elif self.comboBox1.currentItem() == 1:
        		# set-upgrade
        		self.comboBox2.setEnabled(True)
        	elif self.comboBox1.currentItem() == 2:
        		# fetch-update
        		pass
        	elif self.comboBox1.currentItem() == 3:
        		# fetch-upgrade
        		pass
        	elif self.comboBox1.currentItem() == 4:
        		# install-update
        		pass
        	elif self.comboBox1.currentItem() == 5:
        		# install-upgrade
        		pass
        	else:
        		error()
        

    def whichUpgradeOption(self,a0):
        	if self.comboBox2.currentItem() == 0:
        		self.frame3.setEnabled(True)
        

    def __tr(self,s,c = None):
        return qApp.translate("Form1",s,c)
