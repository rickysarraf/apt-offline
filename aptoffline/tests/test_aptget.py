import unittest
import tempfile
import os

from .base import AptOfflineTests
from testtools.matchers import FileContains
from aptoffline.logger import initialize_logger


class AptGetTest(AptOfflineTests):

    def setUp(self):
        super(AptGetTest, self).setUp()
        _, self.outfile = tempfile.mkstemp(dir=self.workdir)
        initialize_logger(False)

    def _run_tests(self, cmd, operation=None, type=None, release=None,
                   packages=None, build_depends=False):
        self.run_aptget_backend(operation, self.outfile, type,
                                release, packages, build_depends)
        stdout, stderr, retcode = self._run_cmd(cmd, allow_fail=False,
                                                universal_newlines=True)
        self.assertThat(self.outfile, FileContains(stdout))

    def test_update(self):
        cmd = 'apt-get -q --print-uris update'.split()
        self._run_tests(cmd, 'update')

    def test_normal_upgrade(self):
        cmd1 = 'apt-get -qq --print-uris upgrade'.split()
        self._run_tests(cmd1, operation='upgrade', type='upgrade')

        cmd2 = 'apt-get -qq --print-uris -t {} upgrade'.format(self.release)
        self._run_tests(cmd2.split(), operation='upgrade', type='upgrade',
                        release=self.release)

    def test_dist_upgrade(self):
        cmd1 = 'apt-get -qq --print-uris dist-upgrade'.split()
        self._run_tests(cmd1, operation='upgrade',
                        type='dist-upgrade')

        cmd2 = 'apt-get -qq --print-uris -t %s dist-upgrade' % self.release
        self._run_tests(cmd2.split(), operation='upgrade',
                        type='dist-upgrade', release=self.release)

    def test_deselect_upgrade(self):
        cmd1 = 'apt-get -qq --print-uris dselect-upgrade'.split()
        self._run_tests(cmd1, operation='upgrade',
                        type='dselect-upgrade')
        cmd2 = 'apt-get -qq --print-uris -t %s dselect-upgrade' % self.release
        self._run_tests(cmd2.split(), operation='upgrade',
                        type='dselect-upgrade', release=self.release)

    def test_install_bin_packages(self):
        cmd1 = ('apt-get -qq --print-uris install '
                'testrepository').split()
        self._run_tests(cmd1, operation='install_bin_packages',
                        packages=['testrepository'])

        cmd2 = ('apt-get -qq --print-uris -t %s '
                'install testrepository') % self.release
        self._run_tests(cmd2.split(),
                        operation='install_bin_packages',
                        packages=['testrepository'],
                        release=self.release)

    def test_install_src_packages(self):
        cmd1 = ('apt-get -qq --print-uris source '
                'bash').split()
        self._run_tests(cmd1, operation='install_src_packages',
                        packages=['bash'])

        cmd2 = ('apt-get -qq --print-uris -t %s'
                ' source bash') % self.release
        self._run_tests(cmd2.split(),
                        operation='install_src_packages',
                        packages=['bash'],
                        release=self.release)

    @unittest.skipIf(os.environ.get('TRAVIS', None),
                     ('Travis uses older apt which has bug with'
                      'build-dep'))
    def test_build_dep(self):
        cmd1 = 'apt-get -qq --print-uris build-dep bash'.split()
        self._run_tests(cmd1, operation='install_src_packages',
                        build_depends=True, packages=['bash'])

        cmd2 = ('apt-get -qq --print-uris -t %s'
                ' build-dep bash') % self.release
        self._run_tests(cmd2.split(), operation='install_src_packages',
                        build_depends=True, packages=['bash'],
                        release=self.release)

    def tearDown(self):
        os.remove(self.outfile)
        super(AptGetTest, self).tearDown()
