#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Copyright 2009 Ritesh Raj Sarraf <rrs@researchut.com>
#
# Licensed under the GNU General Public License v3 and later

import textwrap
import distutils.core

distutils.core.setup(
    name='apt-offline',
    version='0.9.9',
    author='Ritesh Raj Sarraf',
    author_email='rrs@researchut.com',
    url='http://apt-offline.alioth.debian.org',
    #packages = [ 'apt_offline_core' ],
    description='Offline APT Package Manager',
    long_description = textwrap.dedent("""\
        apt-offline is an Offline APT Package Manager
        for Debian and derivatives
        """),
    license='GPL',
    platforms = 'Posix; MacOS X; Windows',
    classifiers=[
        'Development Status :: 3 - Testing/Beta',
        'Environment :: Console',
        'Intended Audience :: End Users',
        'License :: OSI Approved :: GPL',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Package Management',
    ],
    py_modules=['apt_offline_core.AptOfflineCoreLib',
            'apt_offline_core.AptOfflineDebianBtsLib',
#            'apt_offline_core.AptOfflineFetchBugs.py',
            'apt_offline_core.AptOfflineLib',
            'apt_offline_core.AptOfflineMagicLib',
            'apt_offline_core.AptOffline_reportbug_exceptions',
            'apt_offline_core.AptOffline_argparse',
            'apt_offline_core.AptOffline_urlutils',
            'apt_offline_gui.AptOfflineQtAbout.py',
	    'apt_offline_gui.AptOfflineQtCommon.py',
	    'apt_offline_gui.AptOfflineQtCreateProfile.py',
	    'apt_offline_gui.AptOfflineQtFetch.py',
	    'apt_offline_gui.AptOfflineQtInstall.py',
	    'apt_offline_gui.AptOfflineQtMain.py',
	    'apt_offline_gui.AptOfflineQtSaveZip.py',
	    'apt_offline_gui.__init__.py',
	    'apt_offline_gui.QtProgressBar.py',
	    'apt_offline_gui.resources_rc.py',
	    'apt_offline_gui.Ui_AptOfflineQtAbout.py',
	    'apt_offline_gui.Ui_AptOfflineQtCreateProfile.py',
	    'apt_offline_gui.Ui_AptOfflineQtFetch.py',
	    'apt_offline_gui.Ui_AptOfflineQtInstall.py',
	    'apt_offline_gui.Ui_AptOfflineQtMain.py',
	    'apt_offline_gui.Ui_AptOfflineQtSaveZip.py',
	    'apt_offline_gui.UiDataStructs.py',],
    scripts=['apt-offline, apt-offline-gui'],
)
