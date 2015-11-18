from subprocess import check_output, check_call, CalledProcessError

import re

_version_reg = re.compile('Installed:\s(?P<version>.*)\s')


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
