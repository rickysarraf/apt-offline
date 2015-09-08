import os

from .base import AptOfflineTests
from aptoffline.cmdline import main
from aptoffline.logger import initialize_logger
from aptoffline.util import releases, apt_version_compare
from testtools.matchers import (FileExists, GreaterThan, Contains,
                                FileContains)

from tempfile import mkstemp


class TestSetCmd(AptOfflineTests):

    def setUp(self):
        super(TestSetCmd, self).setUp()
        initialize_logger(True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.workdir)
        _, self.sigfile = mkstemp(dir=self.workdir)

    def test_default_sigfile(self):
        main(['set', '--update'])
        self.assertThat('apt-offline.sig', FileExists())

    def test_arbitrary_sigfile(self):
        self.assertEqual(os.stat(self.sigfile).st_size, 0)
        main(['set', self.sigfile, '--upgrade'])

        # Lets see if there is upgrade available for system
        so, se, rc = self._run_cmd(['apt-get', '-qq', '--print-uris',
                                    'upgrade'])
        if len(so) > 0:
            self.assertThat(os.stat(self.sigfile).st_size,
                            GreaterThan(0))
        else:
            # No upgrade, this test is not needed ;-).
            self.assertEqual(os.stat(self.sigfile).st_size, 0)

    def test_release_install_option(self):
        main(['set', '--install-packages', 'ksh', '--release',
              releases[0]])
        self.assertThat('apt-offline.sig', FileExists())
        self.assertThat(os.stat('apt-offline.sig').st_size,
                        GreaterThan(0))

    def test_install_bin_builddep_option(self):
        main(['set', '--install-packages', 'ksh', '--src-build-dep'])
        self.assertThat(
            self.log_details.get(
                "pythonlogging:'apt-offline'").as_text(),
            Contains('ignoring'))

    def test_install_src_packages(self):
        main(['set', '--install-src-packages', 'bash'])
        self.assertThat('apt-offline.sig',
                        FileContains(matcher=Contains('.dsc')))
        self.assertThat('apt-offline.sig',
                        FileContains(matcher=Contains('.tar.gz')))
        self.assertThat('apt-offline.sig',
                        FileContains(matcher=Contains('debian.tar.')))

    def test_install_src_builddep_unprivileged(self):
        if apt_version_compare >= 0:
            self.skipTest('APT bug is solved, so no need of running'
                          'this case')
        main(['set', '--install-src-packages', 'bash',
              '--src-build-dep'])
        log_text = self.log_details.get(
            "pythonlogging:'apt-offline'").as_text()
        print(log_text)
        self.assertThat(log_text, Contains('we need root'))
        self.assertThat(log_text, Contains('Ignoring the operation,'))

    def tearDown(self):
        super(TestSetCmd, self).tearDown()
        os.remove(self.sigfile)
        if os.path.exists('apt-offline.sig'):
            os.remove('apt-offline.sig')
