from subprocess import check_output, check_call, CalledProcessError
from functools import partial

import re
import os


_version_reg = re.compile('Installed:\s(?P<version>.*)\s')


def _parse_sourceslist(file):
    with open(file) as fd:
        s = fd.read()
        return filter(lambda x: not x.startswith('#') and len(x) != 0,
                      map(lambda x: x.strip(), s.split('\n')))


def find_releases():
    """Find releases enabled in sources.list

    This function parses /etc/apt/sources.list and all files under
    /etc/apt/sources.list.d and lists all the releases which are
    enabled.

    Returns a set of releases.
    """
    sources_d = partial(os.path.join, '/etc/apt/sources.list.d')
    slists = (['/etc/apt/sources.list'] +
              list(map(sources_d, os.listdir('/etc/apt/sources.list.d/'))))

    lines = []
    for file in slists:
        lines.append(_parse_sourceslist(file))

    releases = set()
    for line in lines:
        for item in line:
            releases.add(item.split(' ')[2])

    return releases


def find_version(package):
    """Find version of package installed

    Arguments:
        - package -- package whose version needs to be determined

    This function uses apt-cache policy to determine the Installed
    version of the package.
    """
    s = check_output(['apt-cache', 'policy', package],
                     universal_newlines=True)
    m = _version_reg.search(s)
    if m:
        return m.group('version')


def compare_version(a, b):
    """Compare version a with version b

    Compares the version a with version b using dpkg --compare-version
    return -1 if a is less than b, 1 if a is greater than b and 0 if a
    is equal to b.
    """
    try:
        check_call(['dpkg', '--compare-versions', a, 'lt', b])
        return -1
    except CalledProcessError:
        try:
            check_call(['dpkg', '--compare-versions', a, 'gt', b])
            return 1
        except CalledProcessError:
            return 0
