"""Tests for confirming AptGetSigParse functionality.
"""
import os

from .base import AptOfflineTests
from testtools.content import text_content
from testtools.matchers import GreaterThan
from aptoffline.backends.aptget import AptGetSigParse


class TestAptGetSigParse(AptOfflineTests):

    def setUp(self):
        super(TestAptGetSigParse, self).setUp()
        self.sigparse_dir = self.resource_path('sigparse')

    def test_update_sigparse(self):
        parser = AptGetSigParse(os.path.join(self.sigparse_dir,
                                             'update.sig'))
        for item in parser:
            self.addDetail('sigitem', text_content(repr(item)))
            self.assertEqual(item.size, '0')
            self.assertFalse(hasattr(item, 'md5sum'))

    def test_nonupdate_sigparse(self):
        parser = AptGetSigParse(os.path.join(self.sigparse_dir,
                                             'apt-offline.sig'))
        for item in parser:
            self.addDetail('sigitem', text_content(repr(item)))
            self.assertThat(int(item.size), GreaterThan(0))
            self.assertTrue(hasattr(item, 'md5sum'))

    def tearDown(self):
        super(TestAptGetSigParse, self).tearDown()
