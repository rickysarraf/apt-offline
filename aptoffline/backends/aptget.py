# Author: Vasudev Kamath <vasudev@copyninja.info>

"""apt-get backend for apt-offline

This module generates signature file for apt-offline operations using
apt-get command.
"""

from aptoffline import AptOffLine
from subprocess import check_call

import re


__all__ = ['AptGet']

_auth_info_reg = re.compile('(?:(http|https)://)'
                            '(?P<user>.*):(?P<passwd>.*)@')


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


class AptGetSigParse(object):
    '''Parse the signature file generated using apt-get command.

    Arguments:
        - sigfile -- Signature file to parse.
    '''

    __slots__ = ('_list')

    def __init__(self, sigfile):
        self._list = []
        with open(sigfile) as fd:
            for line in fd.readlines():
                self._list.append(AptGetSig(line.strip()))

    def __getitem__(self, index):
        return self._list[index]  # pragma: no cover

    def __setitem__(self, index, value):
        self._list[index] = value  # pragma: no cover

    def __delitem__(self, index):
        self._list.__delitem__(index)  # pragma: no cover

    def __iter__(self):
        return self._list.__iter__()  # pragma: no cover

    def __reversed__(self):
        return self._list.__reversed__()  # pragma: no cover

    def __contains__(self, item):
        return self._list.__contains__(item)  # pragma: no cover

    def __repr__(self):
        return repr(self._list)  # pragma: no cover

    def __len__(self):
        return self._list.__len__()


class AptGetSig(object):
    """Object representing single line of signature file

    This object represents single line of signature file generated by
    apt-get command with --print-uris option.
    """

    __slots__ = ('url', 'file', 'size', 'checksum_type', 'checksum',
                 'user', 'passwd')

    def __init__(self, line):
        items = line.split(' ')

        self.url = items[0].lstrip("'").rstrip("'")
        self.file = items[1]
        self.size = items[2]

        m = _auth_info_reg.search(self.url)
        if m:
            self.user = m.group('user')
            self.passwd = m.group('passwd')

        # Only if its not update database there will be md5sum
        if len(items) > 3:
            self.checksum_type, self.checksum = items[3].split(':')

    def __repr__(self):
        if hasattr(self, 'checksum'):
            return "'{}' {} {} {}:{}".format(self.url, self.file,
                                             self.size,
                                             self.checksum_type,
                                             self.checksum)
        return "'{}' {} {}".format(self.url, self.file, self.size)
