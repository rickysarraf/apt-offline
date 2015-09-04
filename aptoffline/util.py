import apt_pkg
from aptsources.sourceslist import SourcesList


__all__ = ['releases', 'apt_version_compare']


def _releases():
    sources = SourcesList()
    sentries = filter(lambda s: s.dist.strip(), sources.list)
    return {entry.dist for entry in sentries}


def _version_apt():
    apt_pkg.init()
    instversion = apt_pkg.Cache()['apt'].current_ver.ver_str
    return apt_pkg.version_compare(instversion, '1.1~exp9')

releases = _releases()
apt_version_compare = _version_apt()
