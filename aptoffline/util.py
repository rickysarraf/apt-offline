from apt import Cache
from apt_pkg import version_compare
from aptsources.sourceslist import SourcesList


__all__ = ['releases', 'apt_version_compare']


def _releases():
    sources = SourcesList()
    sentries = filter(lambda s: s.dist.strip(), sources.list)
    return {entry.dist for entry in sentries}


def _version_apt():
    instversion = Cache()['apt'].candidate.version
    return version_compare(instversion, '1.1~exp9')

releases = list(_releases())
apt_version_compare = _version_apt()
