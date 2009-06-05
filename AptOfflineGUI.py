# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyptofflinegui.ui'
#
# Created: Fri Dec 28 18:18:28 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.17.3
#
# WARNING! All changes made in this file will be lost!


from qt import *


class pyptofflineguiForm(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setName("pyptofflineguiForm")

        self.setUsesTextLabel(1)

        self.setCentralWidget(QWidget(self,"qt_central_widget"))

        self.pyptTabWidget = QTabWidget(self.centralWidget(),"pyptTabWidget")
        self.pyptTabWidget.setGeometry(QRect(10,0,600,430))

        self.tab = QWidget(self.pyptTabWidget,"tab")

        self.textLabel1 = QLabel(self.tab,"textLabel1")
        self.textLabel1.setGeometry(QRect(110,81,361,80))
        textLabel1_font = QFont(self.textLabel1.font())
        textLabel1_font.setPointSize(48)
        self.textLabel1.setFont(textLabel1_font)

        self.textLabel1_2 = QLabel(self.tab,"textLabel1_2")
        self.textLabel1_2.setGeometry(QRect(150,190,280,24))

        self.textLabel2 = QLabel(self.tab,"textLabel2")
        self.textLabel2.setGeometry(QRect(140,220,291,21))
        self.pyptTabWidget.insertTab(self.tab,QString.fromLatin1(""))

        self.tab_2 = QWidget(self.pyptTabWidget,"tab_2")

        LayoutWidget = QWidget(self.tab_2,"layout20")
        LayoutWidget.setGeometry(QRect(10,20,380,210))
        layout20 = QGridLayout(LayoutWidget,1,1,11,6,"layout20")

        self.setInstallPackageTextLabel = QLabel(LayoutWidget,"setInstallPackageTextLabel")

        layout20.addWidget(self.setInstallPackageTextLabel,2,0)

        self.setUpgradeTypeComboBox = QComboBox(0,LayoutWidget,"setUpgradeTypeComboBox")

        layout20.addWidget(self.setUpgradeTypeComboBox,1,1)

        self.setFilePathLineEdit = QLineEdit(LayoutWidget,"setFilePathLineEdit")
        self.setFilePathLineEdit.setPaletteBackgroundColor(QColor(255,255,255))
        self.setFilePathLineEdit.setAlignment(QLineEdit.AlignAuto)

        layout20.addWidget(self.setFilePathLineEdit,3,1)

        self.pushButton6 = QPushButton(LayoutWidget,"pushButton6")

        layout20.addWidget(self.pushButton6,3,2)

        self.setUpgradeTypeTextLabel = QLabel(LayoutWidget,"setUpgradeTypeTextLabel")

        layout20.addWidget(self.setUpgradeTypeTextLabel,1,0)

        self.setInstallationTypeTextLabel = QLabel(LayoutWidget,"setInstallationTypeTextLabel")

        layout20.addWidget(self.setInstallationTypeTextLabel,0,0)

        self.setFilePathTextLabel = QLabel(LayoutWidget,"setFilePathTextLabel")

        layout20.addWidget(self.setFilePathTextLabel,3,0)

        self.setInstallationTypeComboBox = QComboBox(0,LayoutWidget,"setInstallationTypeComboBox")

        layout20.addWidget(self.setInstallationTypeComboBox,0,1)

        self.setInstallPackagesLineEdit = QLineEdit(LayoutWidget,"setInstallPackagesLineEdit")
        self.setInstallPackagesLineEdit.setPaletteBackgroundColor(QColor(255,255,255))
        setInstallPackagesLineEdit_font = QFont(self.setInstallPackagesLineEdit.font())
        setInstallPackagesLineEdit_font.setBold(1)
        self.setInstallPackagesLineEdit.setFont(setInstallPackagesLineEdit_font)
        self.setInstallPackagesLineEdit.setAlignment(QLineEdit.AlignAuto)

        layout20.addWidget(self.setInstallPackagesLineEdit,2,1)

        self.pushButton5 = QPushButton(self.tab_2,"pushButton5")
        self.pushButton5.setGeometry(QRect(450,350,100,20))

        self.textBrowser3 = QTextBrowser(self.tab_2,"textBrowser3")
        self.textBrowser3.setGeometry(QRect(8,249,381,140))

        self.textLabel3 = QLabel(self.tab_2,"textLabel3")
        self.textLabel3.setGeometry(QRect(8,228,191,21))
        self.pyptTabWidget.insertTab(self.tab_2,QString.fromLatin1(""))

        self.TabPage = QWidget(self.pyptTabWidget,"TabPage")

        LayoutWidget_2 = QWidget(self.TabPage,"layout22")
        LayoutWidget_2.setGeometry(QRect(18,30,340,130))
        layout22 = QGridLayout(LayoutWidget_2,1,1,11,6,"layout22")

        self.fetchUpdateDataRadioButton = QRadioButton(LayoutWidget_2,"fetchUpdateDataRadioButton")

        layout22.addWidget(self.fetchUpdateDataRadioButton,0,0)

        self.fetchUpgradeDataRadioButton = QRadioButton(LayoutWidget_2,"fetchUpgradeDataRadioButton")

        layout22.addWidget(self.fetchUpgradeDataRadioButton,1,0)

        self.fetchBrowseLineEdit = QLineEdit(LayoutWidget_2,"fetchBrowseLineEdit")
        self.fetchBrowseLineEdit.setPaletteBackgroundColor(QColor(255,255,255))

        layout22.addWidget(self.fetchBrowseLineEdit,2,0)

        self.fetchBrowsePushButton = QPushButton(LayoutWidget_2,"fetchBrowsePushButton")

        layout22.addWidget(self.fetchBrowsePushButton,2,1)

        self.fetchProgressBar = QProgressBar(self.TabPage,"fetchProgressBar")
        self.fetchProgressBar.setGeometry(QRect(20,350,340,20))

        self.fetchOptionsButtonGroup = QButtonGroup(self.TabPage,"fetchOptionsButtonGroup")
        self.fetchOptionsButtonGroup.setGeometry(QRect(380,20,190,290))

        self.fetchZipCheckBox = QCheckBox(self.fetchOptionsButtonGroup,"fetchZipCheckBox")
        self.fetchZipCheckBox.setGeometry(QRect(8,23,91,20))
        self.fetchZipCheckBox.setChecked(1)

        self.fetchTargetDownloadFolderPushButton = QPushButton(self.fetchOptionsButtonGroup,"fetchTargetDownloadFolderPushButton")
        self.fetchTargetDownloadFolderPushButton.setGeometry(QRect(150,94,30,21))

        self.fetchZipPushButton = QPushButton(self.fetchOptionsButtonGroup,"fetchZipPushButton")
        self.fetchZipPushButton.setGeometry(QRect(150,44,30,20))

        self.fetchCacheDirectoryPushButton = QPushButton(self.fetchOptionsButtonGroup,"fetchCacheDirectoryPushButton")
        self.fetchCacheDirectoryPushButton.setGeometry(QRect(151,140,30,21))

        self.fetchCacheDirectoryCheckBox = QCheckBox(self.fetchOptionsButtonGroup,"fetchCacheDirectoryCheckBox")
        self.fetchCacheDirectoryCheckBox.setGeometry(QRect(8,119,170,21))

        self.fetchTargetDownloadFolderCheckbox = QCheckBox(self.fetchOptionsButtonGroup,"fetchTargetDownloadFolderCheckbox")
        self.fetchTargetDownloadFolderCheckbox.setGeometry(QRect(8,71,170,21))

        self.fetchCacheDirectoryLineEdit = QLineEdit(self.fetchOptionsButtonGroup,"fetchCacheDirectoryLineEdit")
        self.fetchCacheDirectoryLineEdit.setGeometry(QRect(10,140,140,21))
        self.fetchCacheDirectoryLineEdit.setPaletteBackgroundColor(QColor(255,255,255))

        self.fetchTargetDownloadFolderLineEdit = QLineEdit(self.fetchOptionsButtonGroup,"fetchTargetDownloadFolderLineEdit")
        self.fetchTargetDownloadFolderLineEdit.setGeometry(QRect(8,94,140,21))
        self.fetchTargetDownloadFolderLineEdit.setPaletteBackgroundColor(QColor(255,255,255))

        self.lineEdit7 = QLineEdit(self.fetchOptionsButtonGroup,"lineEdit7")
        self.lineEdit7.setGeometry(QRect(8,44,141,21))
        self.lineEdit7.setPaletteBackgroundColor(QColor(255,255,255))

        self.fetchThreadsSpinBox = QSpinBox(self.fetchOptionsButtonGroup,"fetchThreadsSpinBox")
        self.fetchThreadsSpinBox.setGeometry(QRect(10,260,131,21))
        self.fetchThreadsSpinBox.setMaxValue(5)
        self.fetchThreadsSpinBox.setMinValue(1)

        self.fetchThreadsTextLabel = QLabel(self.fetchOptionsButtonGroup,"fetchThreadsTextLabel")
        self.fetchThreadsTextLabel.setGeometry(QRect(10,240,121,21))

        self.fetchDisableMD5ChecksumCheckBox = QCheckBox(self.fetchOptionsButtonGroup,"fetchDisableMD5ChecksumCheckBox")
        self.fetchDisableMD5ChecksumCheckBox.setGeometry(QRect(10,190,170,21))

        self.checkBox5 = QCheckBox(self.fetchOptionsButtonGroup,"checkBox5")
        self.checkBox5.setGeometry(QRect(10,210,170,21))
        self.checkBox5.setChecked(1)

        self.fetchStartButton = QPushButton(self.TabPage,"fetchStartButton")
        self.fetchStartButton.setGeometry(QRect(450,350,100,20))

        self.fetchTextBrowser = QTextBrowser(self.TabPage,"fetchTextBrowser")
        self.fetchTextBrowser.setGeometry(QRect(20,181,340,160))

        self.fetchConsoleOutputTextLabel = QLabel(self.TabPage,"fetchConsoleOutputTextLabel")
        self.fetchConsoleOutputTextLabel.setGeometry(QRect(20,160,141,20))
        self.pyptTabWidget.insertTab(self.TabPage,QString.fromLatin1(""))

        self.TabPage_2 = QWidget(self.pyptTabWidget,"TabPage_2")

        LayoutWidget_3 = QWidget(self.TabPage_2,"layout24")
        LayoutWidget_3.setGeometry(QRect(30,20,330,130))
        layout24 = QGridLayout(LayoutWidget_3,1,1,11,6,"layout24")

        self.installUpdateDataRadioButton = QRadioButton(LayoutWidget_3,"installUpdateDataRadioButton")

        layout24.addWidget(self.installUpdateDataRadioButton,0,0)

        self.installUpgradeDataRadioButton = QRadioButton(LayoutWidget_3,"installUpgradeDataRadioButton")

        layout24.addWidget(self.installUpgradeDataRadioButton,1,0)

        self.instalBrowsePushButton = QPushButton(LayoutWidget_3,"instalBrowsePushButton")

        layout24.addWidget(self.instalBrowsePushButton,2,1)

        self.installLineEdit = QLineEdit(LayoutWidget_3,"installLineEdit")

        layout24.addWidget(self.installLineEdit,2,0)

        self.textLabel7 = QLabel(self.TabPage_2,"textLabel7")
        self.textLabel7.setGeometry(QRect(30,150,171,31))

        self.installTextBrowser = QTextBrowser(self.TabPage_2,"installTextBrowser")
        self.installTextBrowser.setGeometry(QRect(28,184,331,201))

        self.installStartPushButton = QPushButton(self.TabPage_2,"installStartPushButton")
        self.installStartPushButton.setGeometry(QRect(450,350,100,20))
        self.pyptTabWidget.insertTab(self.TabPage_2,QString.fromLatin1(""))

        self.fileExitAction = QAction(self,"fileExitAction")
        self.helpAboutAction = QAction(self,"helpAboutAction")




        self.MenuBar = QMenuBar(self,"MenuBar")


        self.fileMenu = QPopupMenu(self)
        self.fileMenu.insertSeparator()
        self.fileMenu.insertSeparator()
        self.fileExitAction.addTo(self.fileMenu)
        self.MenuBar.insertItem(QString(""),self.fileMenu,1)

        self.helpMenu = QPopupMenu(self)
        self.helpAboutAction.addTo(self.helpMenu)
        self.helpMenu.insertSeparator()
        self.MenuBar.insertItem(QString(""),self.helpMenu,2)


        self.languageChange()

        self.resize(QSize(618,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.fileExitAction,SIGNAL("activated()"),self.close)
        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)

        self.setInstallPackageTextLabel.setBuddy(self.setInstallPackagesLineEdit)
        self.setUpgradeTypeTextLabel.setBuddy(self.setUpgradeTypeComboBox)
        self.setFilePathTextLabel.setBuddy(self.setFilePathLineEdit)


    def languageChange(self):
        self.setCaption(self.__tr("pypt-offline | Offline Package Manager | (C) Ritesh Raj Sarraf - RESEARCHUT"))
        self.textLabel1.setText(self.__tr("<p align=\"center\">pypt-offline</p>"))
        self.textLabel1_2.setText(self.__tr("<p align=\"center\"><font><font size=\"+1\">Offline Package Manager</font></font></p>"))
        self.textLabel2.setText(self.__tr("<p align=\"center\"><font size=\"+1\">(C) Ritesh Raj Sarraf - RESEARCHUT</font></p>"))
        self.pyptTabWidget.changeTab(self.tab,self.__tr("Welcome"))
        self.setInstallPackageTextLabel.setText(self.__tr("Install Packages"))
        self.setUpgradeTypeComboBox.clear()
        self.setUpgradeTypeComboBox.insertItem(QString.null)
        self.setUpgradeTypeComboBox.insertItem(self.__tr("upgrade"))
        self.setUpgradeTypeComboBox.insertItem(self.__tr("dist-upgrade"))
        self.setUpgradeTypeComboBox.insertItem(self.__tr("dselect-upgrade"))
        QToolTip.add(self.setUpgradeTypeComboBox,self.__tr("Select the type of upgrade you want to perform"))
        QToolTip.add(self.setFilePathLineEdit,self.__tr("Full path to a file you want to write to"))
        self.pushButton6.setText(self.__tr("Browse"))
        self.setUpgradeTypeTextLabel.setText(self.__tr("Upgrade Type"))
        self.setInstallationTypeTextLabel.setText(self.__tr("Installation Type"))
        self.setFilePathTextLabel.setText(self.__tr("File Path"))
        self.setInstallationTypeComboBox.clear()
        self.setInstallationTypeComboBox.insertItem(QString.null)
        self.setInstallationTypeComboBox.insertItem(self.__tr("Update"))
        self.setInstallationTypeComboBox.insertItem(self.__tr("Upgrade"))
        self.setInstallationTypeComboBox.insertItem(self.__tr("Install"))
        QToolTip.add(self.setInstallationTypeComboBox,self.__tr("Select the type of installation you want to perform"))
        QToolTip.add(self.setInstallPackagesLineEdit,self.__tr("Package names separated by space"))
        self.pushButton5.setText(self.__tr("Start"))
        self.pushButton5.setAccel(QKeySequence(QString.null))
        self.textLabel3.setText(self.__tr("textLabel3"))
        self.pyptTabWidget.changeTab(self.tab_2,self.__tr("Set"))
        self.fetchUpdateDataRadioButton.setText(self.__tr("Update Data"))
        QToolTip.add(self.fetchUpdateDataRadioButton,self.__tr("Select this if you want to fetch the package database updates"))
        self.fetchUpgradeDataRadioButton.setText(self.__tr("Upgrade Data"))
        QToolTip.add(self.fetchUpgradeDataRadioButton,self.__tr("Select this if you want to fetch the packages which need to be upgraded/installed"))
        QToolTip.add(self.fetchBrowseLineEdit,self.__tr("Path to the data file that was generated on the disconnected machine"))
        self.fetchBrowsePushButton.setText(self.__tr("Browse"))
        QToolTip.add(self.fetchProgressBar,self.__tr("Not Implemented Yet"))
        self.fetchOptionsButtonGroup.setTitle(self.__tr("Options"))
        self.fetchZipCheckBox.setText(self.__tr("Zip"))
        self.fetchTargetDownloadFolderPushButton.setText(self.__tr("..."))
        self.fetchZipPushButton.setText(self.__tr("..."))
        self.fetchCacheDirectoryPushButton.setText(self.__tr("..."))
        self.fetchCacheDirectoryCheckBox.setText(self.__tr("Cache Directory"))
        self.fetchTargetDownloadFolderCheckbox.setText(self.__tr("Target Download Folder"))
        QToolTip.add(self.fetchCacheDirectoryLineEdit,self.__tr("Check this and specify the cache directory which contains pre-downloaded packages"))
        QToolTip.add(self.fetchTargetDownloadFolderLineEdit,self.__tr("Check this and specify the target download folder where the downloaded data will be saved"))
        QToolTip.add(self.lineEdit7,self.__tr("Check this and specify the full path for zip archive"))
        QToolTip.add(self.fetchThreadsSpinBox,self.__tr("Number of threads you want to spawn"))
        self.fetchThreadsTextLabel.setText(self.__tr("Threads"))
        self.fetchDisableMD5ChecksumCheckBox.setText(self.__tr("Disable MD5 Checksum"))
        QToolTip.add(self.fetchDisableMD5ChecksumCheckBox,self.__tr("Check this if you want to disable MD5 Checksum"))
        self.checkBox5.setText(self.__tr("Fetch Bug Reports"))
        QToolTip.add(self.checkBox5,self.__tr("Check this if you want to download the bug reports"))
        self.fetchStartButton.setText(self.__tr("Start"))
        self.fetchConsoleOutputTextLabel.setText(self.__tr("Console Output"))
        self.pyptTabWidget.changeTab(self.TabPage,self.__tr("Fetch"))
        self.installUpdateDataRadioButton.setText(self.__tr("Update Data"))
        QToolTip.add(self.installUpdateDataRadioButton,self.__tr("Select this to install the package database update"))
        self.installUpgradeDataRadioButton.setText(self.__tr("Upgrade Data"))
        QToolTip.add(self.installUpgradeDataRadioButton,self.__tr("Select this to install/upgrade the packages"))
        self.instalBrowsePushButton.setText(self.__tr("Browse"))
        QToolTip.add(self.installLineEdit,self.__tr("Specify the zip archive or full folder path which contains the downloaded data"))
        self.textLabel7.setText(self.__tr("Console Output"))
        self.installStartPushButton.setText(self.__tr("Start"))
        self.pyptTabWidget.changeTab(self.TabPage_2,self.__tr("Install"))
        self.fileExitAction.setText(self.__tr("Exit"))
        self.fileExitAction.setMenuText(self.__tr("E&xit"))
        self.fileExitAction.setAccel(QString.null)
        self.helpAboutAction.setText(self.__tr("About"))
        self.helpAboutAction.setMenuText(self.__tr("&About"))
        self.helpAboutAction.setAccel(QString.null)
        if self.MenuBar.findItem(1):
            self.MenuBar.findItem(1).setText(self.__tr("&File"))
        if self.MenuBar.findItem(2):
            self.MenuBar.findItem(2).setText(self.__tr("&Help"))


    def fileNew(self):
        print "pyptofflineguiForm.fileNew(): Not implemented yet"

    def fileOpen(self):
        print "pyptofflineguiForm.fileOpen(): Not implemented yet"

    def fileSave(self):
        print "pyptofflineguiForm.fileSave(): Not implemented yet"

    def fileSaveAs(self):
        print "pyptofflineguiForm.fileSaveAs(): Not implemented yet"

    def filePrint(self):
        print "pyptofflineguiForm.filePrint(): Not implemented yet"

    def fileExit(self):
        print "pyptofflineguiForm.fileExit(): Not implemented yet"

    def helpIndex(self):
        print "pyptofflineguiForm.helpIndex(): Not implemented yet"

    def helpContents(self):
        print "pyptofflineguiForm.helpContents(): Not implemented yet"

    def helpAbout(self):
        print "pyptofflineguiForm.helpAbout(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("pyptofflineguiForm",s,c)
