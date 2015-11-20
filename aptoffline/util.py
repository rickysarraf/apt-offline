from zipfile import ZipFile
from logging import getLogger
from aptoffline.aptwrapper import (find_version, compare_version)
from aptoffline.logger import LINE_OVERWRITE_FULL

import threading
import os
import hashlib

__all__ = ['apt_version_compare', 'list_files', 'is_cached',
           'UnsupportedCheckSumType', 'is_checksum_valid',
           'ZipArchiver']


apt_version_compare = compare_version(find_version('apt'), '1.1~exp9')
_log = getLogger('apt-offline')

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
    global _log
    pkgname = aptitem.file.split('_')[0]
    for p, f in list_files(cache_dir):
        if f == aptitem.file:
            if not validate:
                _log.warn('Skipping checksum validation for %s.%s' %
                          (pkgname, LINE_OVERWRITE_FULL))
                return os.path.join(p, f)
            if is_checksum_valid(aptitem.file, aptitem.checksum_type,
                                 aptitem.checksum):
                _log.verbose('Checksum correct for package %s.%s' %
                             (pkgname, LINE_OVERWRITE_FULL))
                return os.path.join(p, f)

            log.verbose('%s checksum mismatch. Skipping file from'
                        ' cache.%s' % (pkgname, LINE_OVERWRITE_FULL))
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

    def add_directory(self, dirname):
        for f, p in list_files(dirname):
            self._z.write(os.path.join(f, p), p)

    def close(self):
        self._z.close()

    def __del__(self):
        self._z.close()
