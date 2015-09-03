import testtools
import fixtures
import subprocess

from subprocess import Popen
from .utils import resource_path, distribution_release
from aptoffline.backends.aptget import AptGet


class AptOfflineTests(testtools.TestCase):

    def setUp(self):
        super(AptOfflineTests, self).setUp()

        # Capture STDOUT
        stdout = self.useFixture(
            fixtures.StringStream('stdout')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))

        # Capture STDERR
        stderr = self.useFixture(
            fixtures.StringStream('stderr')).stream
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))

        self.log_fixture = self.useFixture(
            fixtures.FakeLogger('apt-offline'))

        self.workdir = self.useFixture(fixtures.TempDir()).path
        self.release = distribution_release
        self.resource_path = resource_path

    def run_aptget_backend(self, func, outfile, type=None,
                           release=None, packages=None,
                           build_depends=False):
        apt = AptGet(self.outfile)

        if release:
            apt.release = release

        operation = getattr(apt, func)

        if func == 'upgrade':
            t = type or 'upgrade'
            operation(type=t)
        elif func == 'update':
            operation()
        else:
            if func == 'install_bin_packages':
                operation(packages)
            else:
                operation(packages, build_depends)

    def _run_cmd(self, cmd, allow_fail=True, universal_newlines=False):
        result = _run_command(cmd, universal_newlines)
        if result[2] and not allow_fail:
            raise Exception('Command failed to execute: %s' %
                            result[2])
        return result


def _run_command(cmd, newlines):
    p = Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
              stderr=subprocess.PIPE, universal_newlines=newlines)
    streams = tuple(s.decode('latin1').strip() for s in
                        p.communicate())
    return (streams) + (p.returncode,)
