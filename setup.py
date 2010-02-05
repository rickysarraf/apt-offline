# -*- coding: utf-8 -*-

# Copyright © 2009 Ritesh Raj Sarraf <rrs@researchut.com>
#
# Licensed under the GNU General Public License v3 and later

import textwrap
import distutils.core

import apt_offline_core.AptOfflineDebianBtsLib
import apt_offline_core.AptOffline_argparse
import apt_offline_core.AptOfflineLib
import apt_offline_core.AptOfflineMagicLib
import apt_offline_core.AptOffline_reportbug_exceptions
import apt_offline_core.AptOffline_urlutils
import apt_offline_core.AptOfflineCoreLib

distutils.core.setup(
    name='apt-offline',
    version=apt_offline_core.AptOfflineCoreLib.version,
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
    py_modules=[
            'apt_offline_core.AptOfflineDebianBtsLib',
            'apt_offline_core.AptOffline_argparse',
            'apt_offline_core.AptOfflineLib',
            'apt_offline_core.AptOfflineMagicLib',
            'apt_offline_core.AptOffline_reportbug_exceptions',
            'apt_offline_core.AptOffline_urlutils',
            'apt_offline_core.AptOfflineCoreLib'
            ],
    scripts=['apt-offline'],
)
