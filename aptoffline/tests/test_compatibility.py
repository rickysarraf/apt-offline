import os
import tempfile

from aptoffline.logger import initialize_logger
from testtools.matchers import FileContains
from .base import AptOfflineTests
from .utils import py2version


if py2version:
    # Currently we support only TOX and Travis based tests
    if os.environ.get('TRAVIS', None):
        apt_offline_path = os.path.join('/home/travis/virtualenv/',
                                        'python' +
                                        py2version.group('version'), 'bin',
                                        'apt-offline')
    else:
        # We hope we apt-offline is installed on system
        apt_offline_path = '/usr/bin/apt-offline'


class TestCompatibility(AptOfflineTests):

    def setUp(self):
        super(TestCompatibility, self).setUp()
        _, self.module_out = tempfile.mkstemp(dir=self.workdir)
        _, self.aptoffline_out = tempfile.mkstemp(dir=self.workdir)
        initialize_logger(True)

    def _run_tests(self, op=None, type=None, release=None,
                   packages=None, build_depends=False):
        self.run_aptget_backend(op, self.module_out, type, release,
                                packages, build_depends)

        options = ['set', self.aptoffline_out]

        if release:
            options += ['--release', release]

        if op in ['update', 'upgrade']:
            options.append('--' + op)
            if op == 'upgrade' and type:
                options += ['--upgrade-type', type]
        elif op == 'install_bin_packages':
            options += ['--install-packages'] + packages
        elif op == 'install_src_packages':
            options += ['--install-src-packages'] + packages
            if build_depends:
                options.append('--src-build-dep')

        self._run_cmd(['sudo', apt_offline_path] + options)
        with open(self.aptoffline_out) as fd:
            self.assertThat(self.module_out, FileContains(fd.read()))

        self.truncate_file(self.module_out)
        self._run_cmd(['sudo', 'truncate', '-s', '0',
                       self.aptoffline_out])

    def test_update(self):
        if not py2version:
            self.skipTest(("Current apt-offline doesn't"
                           "work on python3"))
        self._run_tests(op='update')

    def test_upgrade(self):
        if not py2version:
            self.skipTest(("Current apt-offline doesn't"
                           "work on python3"))
        self._run_tests(op='upgrade', type='upgrade')
        self._run_tests(op='upgrade', type='upgrade',
                        release=self.release)

    def test_dist_upgrade(self):
        if not py2version:
            self.skipTest(("Current apt-offline doesn't"
                           "work on python3"))
        self._run_tests(op='upgrade', type='dist-upgrade')
        self._run_tests(op='upgrade', type='dist-upgrade',
                        release=self.release)

    def test_dselect_upgrade(self):
        if not py2version:
            self.skipTest(("Current apt-offline doesn't"
                           "work on python3"))
        self._run_tests(op='upgrade', type='dselect-upgrade')
        self._run_tests(op='upgrade', type='dselect-upgrade',
                        release=self.release)

    def test_install_bin_packages(self):
        if not py2version:
            self.skipTest(("Current apt-offline doesn't"
                           "work on python3"))
        self._run_tests(op='install_bin_packages',
                        packages=['testrepository',
                                  'python-subunit'])
        self._run_tests(op='install_bin_packages',
                        packages=['testrepository',
                                  'python-subunit'],
                        release=self.release)

    def test_install_src_packages(self):
        if not py2version:
            self.skipTest(("Current apt-offline doesn't"
                           "work on python3"))
        self._run_tests(op='install_src_packages', packages=['bash'])
        self._run_tests(op='install_src_packages', packages=['bash'],
                        release=self.release)

    def tearDown(self):
        os.remove(self.module_out)
        os.remove(self.aptoffline_out)
        super(TestCompatibility, self).tearDown()
