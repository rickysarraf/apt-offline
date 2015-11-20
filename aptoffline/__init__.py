from logging import getLogger
from abc import abstractmethod


class AptOffLine(object):

    def __init__(self, output, type=None, release=None):
        self.type = type
        self.log = getLogger('apt-offline')
        self.release = release
        self.writeto = output

    @abstractmethod
    def update(self):
        raise NotImplemented

    @abstractmethod
    def upgrade(self, type="upgrade"):
        raise NotImplemented

    @abstractmethod
    def install_bin_packages(self, packages):
        raise NotImplemented

    @abstractmethod
    def install_src_packages(self, packages, build_depends):
        raise NotImplemented
