all:
	pyuic pyptofflinegui.ui > pyptofflinegui.py
	
clean:
	rm -f pyptofflinegui.py
