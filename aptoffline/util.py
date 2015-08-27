from aptsources.sourceslist import SourcesList

__all__ = ['releases']


def _releases():
    sources = SourcesList()
    sentries = filter(lambda s: s.dist.strip(), sources.list)
    return {entry.dist for entry in sentries}

releases = _releases()
