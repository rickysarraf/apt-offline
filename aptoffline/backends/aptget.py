# Author: Vasudev Kamath <vasudev@copyninja.info>

"""apt-get backend for apt-offline

This module generates signature file for apt-offline operations using
apt-get command.
"""

from aptoffline import AptOffLine
from subprocess import check_call

__all__ = ['AptGet']


class AptGet(AptOffLine):
    """Generates signature file using apt-get command

    Keyword Arguments:

        - simulate -- Do not actually perform any operation just
            simulate.
        - release -- Distribution release to use to generate signature
            file.
    """

    def __init__(self, output, simulate=False, release=None):
        super(AptGet, self).__init__(output, type='apt-get',
                                     release=release)
        self.simulate = True
        self._aptcmd = ['apt-get', '--print-uris']

    def update(self):
        """Generate signature file for apt-get update"""

        self.log.info(('Generating database of files that are '
                       'needed for an update.'))
        with open(self.writeto, 'a') as fd:
            check_call(self._aptcmd + ['-q', 'update'], stdout=fd)
            # TODO: Do we need __FixAptSigs from old apt-offline?.

    def upgrade(self, type="upgrade"):
        """Generate signature file for apt upgrade operation.

        This function is used to generate signature file for one of
        following operation.
            - apt-get upgrade
            - apt-get dist-upgrade
            - apt-get dselect-upgrade

        Keyword Arguments:

            - type -- Type of upgrade, this can be `upgrade`,
                `dist-upgrade`, `dselect-upgrade`.
        """
        _cmd = self._aptcmd
        _cmd.append('-qq')

        if self.release:
            _cmd.append('-t')
            _cmd.append(self.release)

        self.log.info(('Generating database of files that are '
                       'needed for an {}').format(type))
        _cmd.append(type)

        with open(self.writeto, 'a') as fd:
            self.log.debug(' '.join(_cmd))
            check_call(_cmd, stdout=fd)

    def install_bin_packages(self, packages):
        """Generate signature file for apt-get install.

        Generates signature filef or installing given `packages`.
        """
        pkgs = set(packages)
        _cmd = self._aptcmd

        _cmd.append('-qq')
        _cmd.append('install')

        if self.release:
            _cmd.append('-t')
            _cmd.append(self.release)

        with open(self.writeto, 'a') as fd:
            self.log.debug(' '.join(_cmd + list(pkgs)))
            check_call(_cmd + list(pkgs), stdout=fd)

    def install_src_packages(self, packages=None,
                             build_depends=False):
        """Generate signature file for source and build-dep.

        Generates signature file for apt-get source and if
        `build_depends` is `True` updates signature file with apt-get
        build-dep `packages`.

        Keyword Arguments:

            - packages -- Packages whose source and or build-dep is to
                be generated.
            - build_depends -- Whether signature file is to be updated
                to get build dependency of `packages`.
        """
        pkgs = set(packages)
        _cmd = self._aptcmd

        _cmd.append('-qq')
        _cmd.append('source')

        if self.release:
            _cmd.append('-t')
            _cmd.append(self.release)

        with open(self.writeto, 'a') as fd:
            self.log.debug(' '.join(_cmd + list(pkgs)))
            check_call(_cmd + list(pkgs), stdout=fd)

            if build_depends:
                sindex = _cmd.index('source')
                _cmd[sindex] = 'build-dep'

                self.log.debug(' '.join(_cmd + list(pkgs)))
                check_call(_cmd + list(pkgs), stdout=fd)
