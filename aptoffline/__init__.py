import logging
from abc import abstractmethod


class AptOffLine(object):

    def __init__(self, type=None):
        self.type = type
        self.log = logging.getLogger('apt-offline')

    @abstractmethod
    def update(self):
        raise NotImplemented

    @abstractmethod
    def upgrade(self, type="upgrade", release=None):
        raise NotImplemented

    @abstractmethod
    def install_bin_packages(self, packages, release):
        raise NotImplemented

    @abstractmethod
    def install_src_packages(self, packages, release, build_depends):
        raise NotImplemented
