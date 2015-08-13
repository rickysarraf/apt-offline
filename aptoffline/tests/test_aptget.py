import unittest
import tempfile
import subprocess
from aptoffline.backends.aptget import AptGet
from aptoffline.logger import initialize_logger
from aptoffline.tests.utils import resource_path


class AptGetTest(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp(dir=resource_path())
        _, self.outfile = tempfile.mkstemp(dir=self.workdir)
        initialize_logger(False)
        self.release = subprocess.check_output(['lsb_release', '-r',
                                                '-s'],
                                               universal_newlines=True).strip()

    def test_update(self):
        apt = AptGet(self.outfile)
        apt.update()
        op = subprocess.check_output(['apt-get', '-q', '--print-uris',
                                      'update'],
                                     universal_newlines=True)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_normal_upgrade(self):
        apt = AptGet(self.outfile)
        apt.upgrade()
        op = subprocess.check_output(['apt-get', '-qq',
                                      '--print-uris', 'upgrade'],
                                     universal_newlines=True)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)
        apt.release = self.release

    def test_normal_upgrade_release(self):
        apt = AptGet(self.outfile, release=self.release)
        apt.upgrade(type='upgrade')
        opr = subprocess.check_output(['apt-get', '-qq',
                                       '--print-uris',
                                       '-t', self.release,
                                       'upgrade'],
                                      universal_newlines=True)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), opr)


    def test_dist_upgrade(self):
        apt = AptGet(self.outfile)
        apt.upgrade(type='dist-upgrade')
        op = subprocess.check_output(['apt-get', '-qq', '--print-uris',
                                      'dist-upgrade'],
                                     universal_newlines=True)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_dist_upgrade_release(self):
        apt = AptGet(self.outfile, release=self.release)
        apt.upgrade(type='dist-upgrade')
        opr = subprocess.check_output(['apt-get', '-qq',
                                       '--print-uris',
                                       '-t', self.release,
                                       'dist-upgrade'],
                                      universal_newlines=True)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), opr)

    def test_deselect_upgrade(self):
        apt = AptGet(self.outfile)
        apt.upgrade(type='dselect-upgrade')
        op = subprocess.check_output(['apt-get', '-qq',
                                      '--print-uris',
                                      'dselect-upgrade'],
                                     universal_newlines=True)
        with open(self.outfile,'r') as fd:
            self.assertEqual(fd.read(), op)

    def test_deselect_upgrade_release(self):
        apt = AptGet(self.outfile, release=self.release)
        apt.upgrade(type='dselect-upgrade')
        opr = subprocess.check_output(['apt-get', '-qq',
                                       '--print-uris',
                                       '-t', self.release,
                                       'dselect-upgrade'],
                                      universal_newlines=True)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), opr)
        

    def tearDown(self):
        import os
        os.remove(self.outfile)
        os.rmdir(self.workdir)
