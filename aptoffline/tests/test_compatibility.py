import re
import sys
import tempfile
import unittest
import subprocess
from aptoffline.tests.utils import resource_path, distribution_release
from aptoffline.logger import initialize_logger
from aptoffline.backends.aptget import AptGet

py2version = re.match('(?P<version>2\.d\.d)(?:.*)', sys.version)


class TestCompatibility(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp(dir=resource_path())
        _, self.module_out = tempfile.mkstemp(dir=self.workdir())
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
        cmd = ['apt-offline']

        cmd.append(op)
        if cmd in ['set', 'get']:
            cmd.append(self.aptoffline_out)

        cmd = map(cmd.append, options)
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
