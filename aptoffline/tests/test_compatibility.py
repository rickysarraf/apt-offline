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

    @unittest.skipUnless(py2version, ("Current apt-offline doesn't"
                                      "work on python3"))
    def test_update(self):
        self.perform_operation(op='update')
        self.run_aptoffline(op='set', options=['--update'])

        with open(self.module_out) as fm:
            with open(self.aptoffline_out) as fo:
                self.assertEqual(fm.read(), fo.read())

    @unittest.skipUnless(py2version, ("Current apt-offline deosn't"
                                      "work on python3"))
    def test_upgrade(self):
        self.perform_operation(op='upgrade', type='upgrade')
        self.run_aptoffline(op='set', options=['--upgrade'])
        with open(self.module_out) as fm:
            with open(self.aptoffline_out) as fo:
                self.assertEqual(fm.read(), fo.read())

    @unittest.skipUnless(py2version, ("Current apt-offline deosn't"
                                      "work on python3"))
    def test_dist_upgrade(self):
        self.perform_operation(op='upgrade', type='dist-upgrade')
        self.run_aptoffline(op='set', options=['--upgrade',
                                               '--upgrade-type',
                                               'dist-upgrade'])
        with open(self.module_out) as fm:
            with open(self.aptoffline_out) as fo:
                self.assertEqual(fm.read(), fo.read())

    @unittest.skipUnless(py2version, ("Current apt-offline deosn't"
                                      "work on python3"))
    def test_dselect_upgrade(self):
        self.perform_operation(op='upgrade', type='dselect-upgrade')
        self.run_aptoffline(op='set', options=['--upgrade',
                                               '--upgrade-type',
                                               'dselect-upgrade'])
        with open(self.module_out) as fm:
            with open(self.aptoffline_out) as fo:
                self.assertEqual(fm.read(), fo.read())

    def tearDown(self):
        os.remove(self.module_out)
        os.remove(self.aptoffline_out)
        os.rmdir(self.workdir)
