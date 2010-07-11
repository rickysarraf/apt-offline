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
#            'apt_offline_core.AptOfflineGUI',
            'apt_offline_core.AptOfflineLib',
            'apt_offline_core.AptOfflineMagicLib',
            'apt_offline_core.AptOffline_reportbug_exceptions',
            'apt_offline_core.AptOffline_argparse',
            'apt_offline_core.AptOffline_urlutils',],
    scripts=['apt-offline'],
)
