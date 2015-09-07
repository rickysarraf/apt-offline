import os

from .base import AptOfflineTests
from aptoffline.cmdline import main
from aptoffline.logger import initialize_logger
from testtools.matchers import FileExists


class TestSetCmd(AptOfflineTests):

    def setUp(self):
        super(TestSetCmd, self).setUp()
        initialize_logger(True)


    def test_default_sigfile(self):
        main(['set','--update'])
        self.assertThat('apt-offline.sig', FileExists())

    def tearDown(self):
        super(TestSetCmd, self).tearDown()
        if os.path.exists('apt-offline.sig'):
            os.remove('apt-offline.sig')
