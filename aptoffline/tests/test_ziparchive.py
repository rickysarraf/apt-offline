from aptoffline.util import ZipArchiver
from aptoffline.tests.base import AptOfflineTests

import os


class TestZipArchiver(AptOfflineTests):

    def setUp(self):
        super(TestZipArchiver, self).setUp()
        self.zipfiles = self.resource_path('ziparchiver')
        self.zip = ZipArchiver(os.path.join(self.workdir,
                                            'ziptestfile.zip'))

    def _verify_archive(self, filelist):
        self.assertEqual(filelist, self.zip.namelist())

    def test_zipadd(self):
        for file in os.listdir(self.zipfiles):
            self.zip.add(os.path.join(self.zipfiles, file))

        self._verify_archive(os.listdir(self.zipfiles))
        self.zip.close()

    def tearDown(self):
        self.zip.close()
        super(TestZipArchiver, self).tearDown()
