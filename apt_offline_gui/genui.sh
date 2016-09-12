#!/bin/sh
# Todo : after adding a new UI file to dialig, also add
#        its corresponding Ui_ script generator here
#

echo "Compiling Ui files"

for each_file in *.ui;
do
	filename=$(echo $each_file | cut -d "." -f1)
	echo "Compiling file $each_file into Ui_$filename.py";
	pyuic4 $each_file > Ui_$filename.py;
done

#pyuic4 AptOfflineQtMain.ui > Ui_AptOfflineQtMain.py
#pyuic4 AptOfflineQtCreateProfile.ui > Ui_AptOfflineQtCreateProfile.py
#pyuic4  AptOfflineQtFetch.ui > Ui_AptOfflineQtFetch.py
#pyuic4 AptOfflineQtInstall.ui > Ui_AptOfflineQtInstall.py
#pyuic4 AptOfflineQtAbout.ui > Ui_AptOfflineQtAbout.py
#pyuic4  AptOfflineQtFetchOptions.ui > Ui_AptOfflineQtFetchOptions.py
#pyuic4  AptOfflineQtInstallBugList.ui > Ui_AptOfflineQtInstallBugList.py

echo "Compiling Resources files"
pyrcc4 -o resources_rc.py resources.qrc
echo "Done"
