/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you want to add, delete, or rename functions or slots, use
** Qt Designer to update this file, preserving your code.
**
** You should not define a constructor or destructor in this file.
** Instead, write your code in functions called init() and destroy().
** These will automatically be called by the form's constructor and
** destructor.
*****************************************************************************/


void Form1::fileExit()
{

}


void Form1::helpIndex()
{

}


void Form1::helpContents()
{

}


void Form1::helpAbout()
{

}




void Form1::whichOption(int)
{
	if self.comboBox1.currentItem() == 0:
		# set-update
		pass
	elif self.comboBox1.currentItem() == 1:
		# set-upgrade
		self.comboBox2.setEnabled(True)
	elif self.comboBox1.currentItem() == 2:
		# fetch-update
		pass
	elif self.comboBox1.currentItem() == 3:
		# fetch-upgrade
		pass
	elif self.comboBox1.currentItem() == 4:
		# install-update
		pass
	elif self.comboBox1.currentItem() == 5:
		# install-upgrade
		pass
	else:
		error()
}


void Form1::whichUpgradeOption(int)
{
	if self.comboBox2.currentItem() == 0:
		self.frame3.setEnabled(True)
}
