#!/bin/sh
# Todo : after adding a new UI file to dialog, also add
#        its corresponding Ui_ script generator here
#

echo "Compiling Ui files"

for each_file in *.ui;
do
	filename=$(echo $each_file | cut -d "." -f1)
	echo "Compiling file $each_file into Ui_$filename.py";
	pyuic6 $each_file -o Ui_$filename.py;
	# Fix PyQt6 API changes in generated files
	# setTabStopWidth was renamed to setTabStopDistance in PyQt6
	sed -i 's/\.setTabStopWidth(/.setTabStopDistance(/g' Ui_$filename.py
done

echo "Compiling Resources files"
# PyQt6 no longer includes pyrcc6, need to convert qrc file manually or use Qt tools
# Try to find the resource compiler
RCC_COMPILED=false
if command -v rcc-qt6 > /dev/null 2>&1; then
	rcc-qt6 -g python -o resources_rc.py resources.qrc && RCC_COMPILED=true
elif command -v rcc > /dev/null 2>&1; then
	rcc -g python -o resources_rc.py resources.qrc && RCC_COMPILED=true
elif [ -x /usr/lib/qt6/libexec/rcc ]; then
	/usr/lib/qt6/libexec/rcc -g python -o resources_rc.py resources.qrc && RCC_COMPILED=true
else
	echo "Warning: Resource compiler not available, skipping resources compilation"
fi

# Fix the import to use PyQt6 instead of PySide6 (Qt's rcc generates PySide6 code by default)
if [ "$RCC_COMPILED" = true ] && [ -f resources_rc.py ]; then
	sed -i 's/from PySide6 import QtCore/from PyQt6 import QtCore/' resources_rc.py
	echo "Resources compiled and fixed for PyQt6"
fi
echo "Done"
