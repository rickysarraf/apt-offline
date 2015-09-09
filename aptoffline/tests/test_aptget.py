import tempfile
import os

from .base import AptOfflineTests
from testtools.matchers import FileContains
from aptoffline.logger import initialize_logger
from aptoffline.util import apt_version_compare


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
        os.truncate(self.outfile, 0)

    def _run_builddep_tests(self, packages, release=None):
        if not release:
            cmd1 = ('apt-get -qq --print-uris source '
                    '%s') % ' '.join(packages)
            cmd2 = ('apt-get -qq --print-uris build-dep '
                    '%s' % ' '.join(packages))
        else:
            cmd1 = ('apt-get -qq --print-uris -t %s'
                    ' source %s') % (self.release,
                                     ' '.join(packages))
            cmd2 = ('apt-get -qq --print-uris -t %s '
                    'build-dep %s') % (self.release,
                                       ' '.join(packages))
        so, se, ret = self._run_cmd(cmd1.split(), False, True)
        bo, be, ret = self._run_cmd(cmd2.split(), False, True)
        self.run_aptget_backend('install_src_packages', self.outfile,
                                release=release, packages=packages,
                                build_depends=True)
        self.assertThat(self.outfile, FileContains(so + bo))
        os.truncate(self.outfile, 0)

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

    def test_build_dep(self):
        if apt_version_compare < 0:
            self.skipTest('apt < 1.1~exp9 requires super user'
                          'privilege for build-dep even with'
                          '--print-uris')

        self._run_builddep_tests(['bash'])
        self._run_builddep_tests(['bash'], self.release)

    def tearDown(self):
        os.remove(self.outfile)
        super(AptGetTest, self).tearDown()
