all: build html

gui:
	cd apt_offline_gui ; ./genui.sh || exit 1

build:gui
	python3 setup.py build

install:
	python3 setup.py install

html:
	man2html apt-offline.8 > apt-offline.html
	
clean:
	rm -f apt_offline_gui/Ui_*.py
	rm -f apt_offline_gui/resources_rc.py
	rm -f *.pyc
	rm -rf build/
	rm -f apt-offline.html
