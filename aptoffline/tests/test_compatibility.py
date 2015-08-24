import re
import sys
import os
import tempfile
import unittest
import subprocess
from aptoffline.tests.utils import resource_path, distribution_release
from aptoffline.logger import initialize_logger
from aptoffline.backends.aptget import AptGet

py2version = re.match('(?P<version>2\.\d\.\d)(?:.*)', sys.version)

if py2version:
    # Currently we support only TOX and Travis based tests
    if os.environ.get('TRAVIS', None):
        apt_offline_path = os.path.join('/home/travis/virtualenv/',
                                        'python' +
                                        py2version.group('version'), 'bin',
                                        'apt-offline')
    else:
        # We hope we apt-offline is installed on system
        apt_offline_path = '/usr/bin/apt-offline'


class TestCompatibility(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp(dir=resource_path())
        _, self.module_out = tempfile.mkstemp(dir=self.workdir)
        _, self.aptoffline_out = tempfile.mkstemp(dir=self.workdir)
        initialize_logger(True)
        self.release = distribution_release

    def perform_operation(self, op=None, type=None, release=None,
                          packages=None):
        apt = AptGet(self.module_out)

        if release:
            apt.release = release

        operation = getattr(apt, op)

        if op == 'upgrade':
            operation(type=type)
        elif op == 'update':
            operation()
        else:
            operation(packages=packages)

    def run_aptoffline(self, op=None, options=None):
        cmd = ['sudo', apt_offline_path]

        cmd.append(op)
        if op in ['set', 'get']:
            cmd.append(self.aptoffline_out)

        map(cmd.append, options)
        subprocess.check_call(cmd)

    def run_tests(self, op=None, type=None, release=None,
                  packages=None):
        if op == 'update':
            self.perform_operation(op='update')
            self.run_aptoffline(op='set', options=['--update'])
        elif op == 'upgrade':
            self.perform_operation(op='upgrade', type=type,
                                   release=release)
            options = ['--upgrade']
            if type and type != 'upgrade':
                options += ['--upgrade-type', type]

            if release:
                options += ['--release', release]

            self.run_aptoffline(op='set', options=options)
        elif op == 'install':
            self.perform_operation(op='install_bin_packages',
                                   packages=packages, release=release)
            options = ['--install-packages'] + packages
            if release:
                options += ['--release', release]

            self.run_aptoffline(op='set', options=options)

        with open(self.module_out) as fm:
            with open(self.aptoffline_out) as fo:
                self.assertEqual(fm.read(), fo.read())

    @unittest.skipUnless(py2version, ("Current apt-offline doesn't"
                                      "work on python3"))
    def test_update(self):
        self.run_tests(op='update')

    @unittest.skipUnless(py2version, ("Current apt-offline deosn't"
                                      "work on python3"))
    def test_upgrade(self):
        self.run_tests(op='upgrade', type='upgrade')
        self.run_tests(op='upgrade', type='upgrade',
                       release=self.release)

    @unittest.skipUnless(py2version, ("Current apt-offline deosn't"
                                      "work on python3"))
    def test_dist_upgrade(self):
        self.run_tests(op='upgrade', type='dist-upgrade')
        self.run_tests(op='upgrade', type='dist-upgrade',
                       release=self.release)

    @unittest.skipUnless(py2version, ("Current apt-offline deosn't"
                                      "work on python3"))
    def test_dselect_upgrade(self):
        self.run_tests(op='upgrade', type='dselect-upgrade')
        self.run_tests(op='upgrade', type='dselect-upgrade',
                       release=self.release)

    @unittest.skipUnless(py2version, ("Current apt-offline deosn't"
                                      "work on python3"))
    def test_install_bin_packages(self):
        self.run_tests(op='install', packages=['testrepository',
                                               'python-subunit'])
        self.run_tests(op='install', packages=['testrepository',
                                               'python-subunit'],
                       release=self.release)

    def tearDown(self):
        os.remove(self.module_out)
        os.remove(self.aptoffline_out)
        os.rmdir(self.workdir)
