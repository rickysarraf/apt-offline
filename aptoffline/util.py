from zipfile import ZipFile

_python_apt = True
try:
    from apt import Cache
    from apt_pkg import version_compare
    from aptsources.sourceslist import SourcesList
except ImportError:
    _python_apt = False
    from aptoffline.aptwrapper import (find_releases, find_version,
                                       compare_version)

import threading
import os

__all__ = ['releases', 'apt_version_compare']


def _releases():
    sources = SourcesList()
    sentries = filter(lambda s: s.dist.strip(), sources.list)
    return {entry.dist for entry in sentries}


def _version_apt():
    instversion = Cache()['apt'].candidate.version
    return version_compare(instversion, '1.1~exp9')

releases = list(_releases()) if _python_apt else list(find_releases())
apt_version_compare = (_version_apt() if _python_apt else
                       compare_version(find_version('apt'),
                                       '1.1~exp9'))


class ZipArchiver(object):
    """Zip Archiver class for apt-offline

    Arguments:
        - filename -- Zip file name.

    This object is used to create zip bundle of downloaded files by
    apt-offline. This class is used when `--bundle` option is provided
    from commandline.
    """

    def __init__(self, filename):
        self._lock = threading.Lock()
        self._z = ZipFile(filename, mode='w')

    def add(self, file):
        if self._lock.acquire():
            self._z.write(file, os.path.basename(file))
            self._lock.release()

    def namelist(self):
        return self._z.namelist()

    def close(self):
        self._z.close()

    def __del__(self):
        self._z.close()
