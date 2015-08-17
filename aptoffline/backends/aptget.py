import subprocess
import re
from aptoffline import AptOffLine
from subprocess import check_call, Popen

__all__ = ['AptGet']


class AptGet(AptOffLine):

    def __init__(self, output, simulate=False, reinstall=False, release=None):
        super(AptGet, self).__init__(output, type='apt-get',
                                     reinstall=reinstall,
                                     release=release)
        self.simulate = True
        self._aptcmd = ['apt-get', '--print-uris']
        self._autoremove_regex = re.compile("(?:.*?no longer required:)"
                                            "(?P<packages>.*?)"
                                            "(?:Use 'apt-get autoremove'.*?)")

    def update(self):
        self.log.info(('Generating database of files that are '
                       'needed for an update.'))
        with open(self.writeto, 'w') as fd:
            check_call(self._aptcmd + ['-q', 'update'], stdout=fd)
            # TODO: Do we need __FixAptSigs from old apt-offline?.

    def upgrade(self, type="upgrade"):
        _cmd = self._aptcmd
        _cmd.append('-qq')

        if self.release:
            _cmd.append('-t')
            _cmd.append(self.release)

        self.log.info(('Generating database of files that are '
                       'needed for an {}').format(type))
        _cmd.append(type)

        with open(self.writeto, 'w') as fd:
            self.log.debug(' '.join(_cmd))
            check_call(_cmd, stdout=fd)

    def install_bin_packages(self, packages):
        pkgs = set(packages)
        _cmd = self._aptcmd

        _cmd.append('-qq')
        _cmd.append('install')

        if self.reinstall:
            _cmd.append('--reinstall')
            pkgs.update(list(self._get_installed_pkg_deps(pkgs)))

        if self.release:
            _cmd.append('-t')
            _cmd.append(self.release)

        with open(self.writeto, 'w') as fd:
            self.log.debug(' '.join(_cmd + list(pkgs)))
            check_call(_cmd + list(pkgs), stdout=fd)

    def install_src_packages(self, packages, build_depends):
        pass

    def _get_installed_pkg_deps(self, pkgs):
        try:
            check_call(['apt-get', 'clean', '&&', 'apt-get', 'autoremove',
                        '-y'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            self.log.critical(e)
            import sys
            sys.exit(2)

        for pkg in pkgs:
            apt = Popen(['apt-get', '-s', 'remove', pkg, '--assume-no'],
                        stdout=subprocess.PIPE)
            tr = Popen(['tr', '\n', ' '], stdin=apt.stdout,
                       stdout=subprocess.PIPE,
                       universal_newlines=True)
            apt.stdout.close()
            op, err = tr.communicate()
            if err:
                self.log.error('Failed to get dependency for package:'
                               '{}'.format(pkg))
                self.log.error('Error message {}'.format(err))

            match = self._autoremove_regex.search(op)
            if match:
                for p in match.group('packages').strip().split():
                    yield p
