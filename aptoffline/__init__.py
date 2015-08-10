from abc import abstractmethod


class AptOffLine(object):

    @abstractmethod
    def update(self):
        raise NotImplementedError

    @abstractmethod
    def upgrade(self, type="upgrade", release=None):
        raise NotImplementedError

    @abstractmethod
    def install_bin_packages(self, packages, release):
        raise NotImplementedError

    @abstractmethod
    def install_src_packages(self, packages, release, build_depends):
        raise NotImplementedError
