#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Copyright © 2009 Ritesh Raj Sarraf <rrs@researchut.com>
#
# Licensed under the GNU General Public License v3 and later

import textwrap
import distutils.core

import AptOfflineCoreLib
import AptOfflineDebianBtsLib
#import AptOfflineFetchBugs
#import AptOfflineGUI
import AptOfflineLib
import AptOfflineMagicLib
import AptOffline_reportbug_exceptions
import AptOffline_urlutils
import AptOffline_argparse

distutils.core.setup(
    name='apt-offline',
    version=AptOfflineCoreLib.version,
    author='Ritesh Raj Sarraf',
    author_email='rrs@researchut.com',
    url='http://apt-offline.alioth.debian.org',
    description='Offline APT Package Manager',
    long_description = textwrap.dedent("""\
        apt-offline is an Offline APT Package Manager
        for Debian and derivatives
        """),
    license='GPL',
    classifiers=[
        'Development Status :: 3 - Testing/Beta',
        'Environment :: Console',
        'Intended Audience :: End Users',
        'License :: OSI Approved :: GPL',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Package Management',
    ],
    py_modules=['AptOfflineCoreLib',
            'AptOfflineDebianBtsLib',
#            'AptOfflineFetchBugs.py',
#            'AptOfflineGUI',
            'AptOfflineLib',
            'AptOfflineMagicLib',
            'AptOffline_reportbug_exceptions',
            'AptOffline_argparse',
            'AptOffline_urlutils',],
    scripts=['apt-offline'],
    data_files = [('share/man/man8',['apt-offline.8']),
            ('share/doc/apt-offline',['apt-offline.html',
                    'README', 'THANKS', 'INSTALL', 'LICENSE'])],
)
