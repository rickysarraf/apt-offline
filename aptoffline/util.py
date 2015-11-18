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
import hashlib

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


def list_files(pathname):
    """Lists files in given path

    This function returns a tuple of absolute path and file name
    (basename of file) in it.
    """
    for path, folder, files in os.walk(pathname):
        for file in files:
            yield path, file


def is_cached(cache_dir, aptitem, validate=True):
    """Check if given apt item is cached

    Arguments:
        - cache_dir -- Directory which contains downloaded files
        - aptitem -- This object of type `AptGetSig`
        - validate -- Whether checksum is to be validated or not.

    Function verifies if the given deb file is already present in
    `cache_dir` and if `validate` is true it checks if the data
    checksum matches `aptitem.checksum`.
    """
    for p, f in list_files(cache_dir):
        if f == aptitem.file:
            if not validate:
                return os.path.join(p, f)
            if is_checksum_valid(aptitem.file, aptitem.checksum_type,
                                 aptitem.checksum):
                return os.path.join(p, f)

            return None


class UnsupportedCheckSumType(Exception):
    """Unsupported Checksum Type exception

    Arguments:
        - type -- Checksum type which lead to this exception.
    """
    def __init__(self, type):
        super(UnsupportedCheckSumType, self).__init__(
            ("Checksum {} is "
             "not supported").format(type))


def is_checksum_valid(filename, checksum_type, checksum):
    """Check if given file is still valid

    This function varifies the calculated checksum of content of file
    against given `checksum`. It returns `true` if both match
    otherwise returns 'false'

    If `checksum_type` is not one of `hashlib.algorithms_guaranteed`
    it will raise `UnsupportedCheckSumType` exception.
    """
    if not hasattr(hashlib, checksum_type.lower()):
        raise UnsupportedCheckSumType(checksum_type)
    csum = getattr(hashlib, checksum_type)

    with open(filename, 'rb') as fd:
        if csum(fd.read()).hexdigest() == checksum:
            return True

    return False


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
