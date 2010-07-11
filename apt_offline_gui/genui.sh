#!/bin/sh
echo "Compiling Ui files"
pyuic4 AptOfflineQtMain.ui > Ui_AptOfflineQtMain.py
pyuic4 AptOfflineQtCreateProfile.ui > Ui_AptOfflineQtCreateProfile.py
pyuic4  AptOfflineQtFetch.ui > Ui_AptOfflineQtFetch.py
pyuic4 AptOfflineQtInstall.ui > Ui_AptOfflineQtInstall.py
pyuic4 AptOfflineQtAbout.ui > Ui_AptOfflineQtAbout.py
echo "Done"
