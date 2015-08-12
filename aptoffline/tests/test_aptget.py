import unittest
import tempfile
import subprocess
from aptoffline.backends.aptget import AptGet
from aptoffline.tests.utils import resource_path


class AptGetTest(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp(dir=resource_path())
        _, self.outfile = tempfile.mkstemp(dir=self.workdir)

    def test_update(self):
        apt = AptGet(self.outfile)
        apt.update()
        op = subprocess.check_output(['apt-get', '-q', '--print-uris',
                                      'update'],
                                     universal_newlines=True)
        with open(self.outfile, 'r') as fd:
            self.assertEqual(fd.read(), op)

    def tearDown(self):
        import os
        os.remove(self.outfile)
        os.rmdir(self.workdir)
