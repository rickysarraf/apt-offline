all:
	pyuic AptOfflineGUI.ui > AptOfflineGUI.py
	
clean:
	rm -f AptOfflineGUI.py
