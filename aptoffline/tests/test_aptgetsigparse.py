"""Tests for confirming AptGetSigParse functionality.
"""
import os

from .base import AptOfflineTests
from functools import partial
from testtools.content import text_content
from testtools.matchers import GreaterThan
from aptoffline.backends.aptget import AptGetSigParse


class TestAptGetSigParse(AptOfflineTests):

    def setUp(self):
        super(TestAptGetSigParse, self).setUp()
        self.sigparse_dir = partial(self.resource_path, 'sigparse')

    def test_update_sigparse(self):
        parser = AptGetSigParse(os.path.join(self.sigparse_dir(
            'update.sig')))
        for item in parser:
            self.addDetail('sigitem', text_content(repr(item)))
            self.assertEqual(item.size, '0')
            self.assertFalse(hasattr(item, 'checksum'))

    def test_nonupdate_sigparse(self):
        parser = AptGetSigParse(self.sigparse_dir('apt-offline.sig'))
        for item in parser:
            self.addDetail('sigitem', text_content(repr(item)))
            self.assertThat(int(item.size), GreaterThan(0))
            self.assertTrue(hasattr(item, 'checksum'))
            self.assertTrue(hasattr(item, 'checksum_type'))

    def test_parsed_updatevalues(self):
        parser = AptGetSigParse(self.sigparse_dir('update-1line.sig'))
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser[0].url,
                         'http://172.16.10.1:9999/debian/dists/sid/'
                         'main/binary-i386/Packages.bz2')
        self.assertEqual(parser[0].file,
                         '172.16.10.1:9999_debian_dists_sid'
                         '_main_binary-i386_Packages')
        self.assertEqual(int(parser[0].size), 0)
        self.assertFalse(hasattr(parser[0], 'checksum'))

    def test_parsed_nonupdatevalues(self):
        parser = AptGetSigParse(
            self.sigparse_dir('install-1line.sig'))
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser[0].url,
                         'http://172.16.10.1:9999/debian/pool/'
                         'main/g/graphite2/libgraphite2-3_'
                         '1.2.4-3_i386.deb')
        self.assertEqual(parser[0].file,
                         'libgraphite2-3_1.2.4-3_i386.deb')
        self.assertEqual(int(parser[0].size),
                         57966)
        self.assertEqual(parser[0].checksum_type, 'MD5Sum')
        self.assertEqual(parser[0].checksum,
                         '9b85dcfb537b09b7ccac4a68e164429c')

    def tearDown(self):
        super(TestAptGetSigParse, self).tearDown()
