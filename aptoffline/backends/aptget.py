from aptoffline import AptOffLine
from subprocess import check_call

__all__ = ['AptGet']


class AptGet(AptOffLine):

    def __init__(self, output, simulate=False, release=None):
        super(AptGet, self).__init__(output, type='apt-get',
                                     release=release)
        self.simulate = True
        self._aptcmd = ['apt-get', '--print-uris']

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

        if self.release:
            _cmd.append('-t')
            _cmd.append(self.release)

        with open(self.writeto, 'w') as fd:
            self.log.debug(' '.join(_cmd + list(pkgs)))
            check_call(_cmd + list(pkgs), stdout=fd)

    def install_src_packages(self, packages, build_depends):
        pass
