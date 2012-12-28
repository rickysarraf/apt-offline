#!/bin/sh
# Todo : after adding a new UI file to dialig, also add
#        its corresponding Ui_ script generator here
#

echo "Compiling Ui files"
pyuic4 AptOfflineQtMain.ui > Ui_AptOfflineQtMain.py
pyuic4 AptOfflineQtCreateProfile.ui > Ui_AptOfflineQtCreateProfile.py
pyuic4  AptOfflineQtFetch.ui > Ui_AptOfflineQtFetch.py
pyuic4 AptOfflineQtInstall.ui > Ui_AptOfflineQtInstall.py
pyuic4 AptOfflineQtAbout.ui > Ui_AptOfflineQtAbout.py
pyuic4  AptOfflineQtFetchOptions.ui > Ui_AptOfflineQtFetchOptions.py
pyuic4  AptOfflineQtInstallBugList.ui > Ui_AptOfflineQtInstallBugList.py
echo "Done"
