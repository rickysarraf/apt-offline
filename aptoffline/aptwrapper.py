from subprocess import check_output, check_call, CalledProcessError

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
    slists = (['/etc/apt/sources.list'] +
              os.listdir('/etc/apt/sources.list.d/'))

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
    """Compare version a with version b using operation op

    Compares the version a with version b using dpkg --compare-version
    return 0 if operation holds otherwise 1
    """
    try:
        check_call(['dpkg', '--compare-versions', a, 'lt', b])
        return -1
    except CalledProcessError as c:
        try:
            check_call(['dpkg', '--compare-versions', a, 'gt', b])
            return 1
        except CalledProcessError as c:
            return 0

    return retcode
