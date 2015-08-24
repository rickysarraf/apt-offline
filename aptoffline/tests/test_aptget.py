import unittest
import tempfile
import subprocess
from aptoffline.backends.aptget import AptGet
from aptoffline.logger import initialize_logger
from aptoffline.tests.utils import resource_path, distribution_release


class AptGetTest(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp(dir=resource_path())
        _, self.outfile = tempfile.mkstemp(dir=self.workdir)
        initialize_logger(False)
        self.release = distribution_release

    def _perform_operation(self, operation=None, type=None,
                           release=None, packages=None):
        if operation not in ['update', 'upgrade',
                             'install_bin_packages',
                             'install_src_packages']:
            return
        apt = AptGet(self.outfile)
        quiet = '-q' if operation == 'update' else '-qq'
        cmd = ['apt-get', quiet, '--print-uris']

        if release:
            apt.release = release
            cmd.append('-t')
            cmd.append(release)

        # Get the function
        func = getattr(apt, operation)
        if operation == 'upgrade':
            cmd.append(type)
            func(type=type)
        elif operation == 'update':
            cmd.append(operation)
            func()
        else:
            # install packages
            # TODO: need to handle source packages
            cmd.append('install')
            cmd = cmd + packages
            func(packages)

        return subprocess.check_output(cmd, universal_newlines=True)

    def _run_tests(self, operation=None, type=None, release=None,
                   packages=None):
        op = self._perform_operation(operation=operation, type=type,
                                     release=release,
                                     packages=packages)
        with open(self.outfile) as fd:
            self.assertEqual(fd.read(), op)

    def test_update(self):
        self._run_tests('update')

    def test_normal_upgrade(self):
        self._run_tests(operation='upgrade', type='upgrade')
        self._run_tests(operation='upgrade', type='upgrade',
                        release=self.release)

    def test_dist_upgrade(self):
        self._run_tests(operation='upgrade', type='dist-upgrade')
        self._run_tests(operation='upgrade', type='dist-upgrade',
                        release=self.release)

    def test_deselect_upgrade(self):
        self._run_tests(operation='upgrade', type='dselect-upgrade')
        self._run_tests(operation='upgrade', type='dselect-upgrade',
                        release=self.release)

    def test_install_bin_packages(self):
        self._run_tests(operation='install_bin_packages',
                        packages=['testrepository',
                                  'python-subunit'])
        self._run_tests(operation='install_bin_packages',
                        packages=['testrepository',
                                  'python-subunit'],
                        release=self.release)

    def tearDown(self):
        import os
        os.remove(self.outfile)
        os.rmdir(self.workdir)
