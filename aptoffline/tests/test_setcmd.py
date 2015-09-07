import os

from .base import AptOfflineTests
from aptoffline.cmdline import main
from aptoffline.logger import initialize_logger
from testtools.matchers import FileExists, GreaterThan
from tempfile import mkstemp


class TestSetCmd(AptOfflineTests):

    def setUp(self):
        super(TestSetCmd, self).setUp()
        initialize_logger(True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.workdir)
        _, self.sigfile = mkstemp(dir=self.workdir)

    def test_default_sigfile(self):
        main(['set','--update'])
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


    def tearDown(self):
        super(TestSetCmd, self).tearDown()
        os.remove(self.sigfile)
        if os.path.exists('apt-offline.sig'):
            os.remove('apt-offline.sig')
