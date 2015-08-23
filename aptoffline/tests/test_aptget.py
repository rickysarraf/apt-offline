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

    def perform_operation(self, operation=None, type=None,
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

    def test_update(self):
        op = self.perform_operation(operation='update')
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_normal_upgrade(self):
        op = self.perform_operation(operation='upgrade', type='upgrade')
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_normal_upgrade_release(self):
        op = self.perform_operation(operation='upgrade',
                                    type='upgrade', release=self.release)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_dist_upgrade(self):
        op = self.perform_operation(operation='upgrade',
                                    type='dist-upgrade')
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_dist_upgrade_release(self):
        op = self.perform_operation(operation='upgrade',
                                    type='dist-upgrade',
                                    release=self.release)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_deselect_upgrade(self):
        op = self.perform_operation(operation='upgrade',
                                    type='dselect-upgrade')
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_deselect_upgrade_release(self):
        op = self.perform_operation(operation='upgrade',
                                    type='dselect-upgrade',
                                    release=self.release)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_install_bin_packages(self):
        op = self.perform_operation(operation='install_bin_packages',
                                    packages=['testrepository',
                                              'python-subunit'])
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_install_bin_packages_release(self):
        op = self.perform_operation(operation='install_bin_packages',
                                    packages=['testrepository',
                                              'python-subunit'],
                                    release=self.release)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def tearDown(self):
        import os
        os.remove(self.outfile)
        os.rmdir(self.workdir)
