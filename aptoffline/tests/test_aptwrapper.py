from testtools import TestCase
from apt import Cache
from apt_pkg import version_compare
from aptsources.sourceslist import SourcesList
from aptoffline.aptwrapper import (find_releases, find_version,
                                   compare_version)


class TestAptWrapper(TestCase):

    def setUp(self):
        super(TestAptWrapper, self).setUp()
        self.sources = SourcesList()
        self.cache = Cache()

    def test_find_releases(self):
        r1 = find_releases()
        sentries = filter(lambda s: s.dist.strip(), self.sources.list)
        r2 = {entry.dist for entry in sentries}
        self.assertEqual(r1, r2)

    def test_find_version(self):
        v1 = find_version('apt')
        v2 = self.cache['apt'].candidate.version
        self.assertEqual(v1, v2)

    def test_compare_version(self):
        c1 = compare_version('1.0', '1.1~exp11')
        c2 = version_compare('1.0', '1.1~exp11')
        self.assertEqual(c1, -1)
        self.assertEqual(c1, c2)

        c3 = compare_version('1.1~exp12', '1.1~exp11')
        c4 = version_compare('1.1~exp12', '1.1~exp11')
        self.assertEqual(c3, 1)
        self.assertEqual(c3, c4)

        c5 = compare_version('1.0', '1.0')
        c6 = version_compare('1.0', '1.0')
        self.assertEqual(c5, 0)
        self.assertEqual(c5, c6)

    def tearDown(self):
        super(TestAptWrapper, self).tearDown()
