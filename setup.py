#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# Copyright 2009 Ritesh Raj Sarraf <rrs@researchut.com>
#
# Licensed under the GNU General Public License v3 and later

import textwrap
import distutils.core

distutils.core.setup(
    name='apt-offline',
    version='1.8.5',
    author='Ritesh Raj Sarraf',
    author_email='rrs@researchut.com',
    url='https://github.com/rickysarraf/apt-offline',
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
            'apt_offline_core.AptOfflineLib',
            'apt_offline_core.AptOfflineMagicLib',
            'apt_offline_gui.AptOfflineQtAbout',
	    'apt_offline_gui.AptOfflineQtCommon',
	    'apt_offline_gui.AptOfflineQtCreateProfile',
	    'apt_offline_gui.AptOfflineQtFetch',
	    'apt_offline_gui.AptOfflineQtFetchOptions',
	    'apt_offline_gui.AptOfflineQtInstall',
	    'apt_offline_gui.AptOfflineQtInstallBugList',
	    'apt_offline_gui.AptOfflineQtInstallChangelog',
	    'apt_offline_gui.AptOfflineQtMain',
	    'apt_offline_gui.AptOfflineQtSaveZip',
	    'apt_offline_gui.__init__',
	    'apt_offline_gui.QtProgressBar',
	    'apt_offline_gui.resources_rc',
	    'apt_offline_gui.Ui_AptOfflineQtAbout',
	    'apt_offline_gui.Ui_AptOfflineQtCreateProfile',
	    'apt_offline_gui.Ui_AptOfflineQtFetch',
	    'apt_offline_gui.Ui_AptOfflineQtFetchOptions',
	    'apt_offline_gui.Ui_AptOfflineQtInstall',
	    'apt_offline_gui.Ui_AptOfflineQtInstallBugList',
	    'apt_offline_gui.Ui_AptOfflineQtInstallChangelog',
	    'apt_offline_gui.Ui_AptOfflineQtMain',
	    'apt_offline_gui.Ui_AptOfflineQtSaveZip',
	    'apt_offline_gui.UiDataStructs',],
    scripts=['apt-offline', 'apt-offline-gui', 'apt-offline-gui-pkexec'],
)
