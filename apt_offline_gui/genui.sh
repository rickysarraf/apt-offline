#!/bin/sh
# Todo : after adding a new UI file to dialog, also add
#        its corresponding Ui_ script generator here
#

echo "Compiling Ui files"

for each_file in *.ui;
do
	filename=$(echo $each_file | cut -d "." -f1)
	echo "Compiling file $each_file into Ui_$filename.py";
	pyuic5 --from-imports $each_file -o Ui_$filename.py;
done

echo "Compiling Resources files"
pyrcc5 -o resources_rc.py resources.qrc
echo "Done"
