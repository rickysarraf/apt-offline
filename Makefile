all:
	@echo "To build GUI, run make gui"

gui:
	pyuic AptOfflineGUI.ui > AptOfflineGUI.py
	
clean:
	rm -f AptOfflineGUI.py
