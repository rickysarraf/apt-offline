import os
import sys
import subprocess
from functools import partial
from re import match

__all__ = ['resource_path', 'distribution_release', 'py2version']

resource_path = partial(os.path.join, os.path.dirname(__file__),
                        'resources')

distribution_release = subprocess.check_output(['lsb_release', '-c',
                                                '-s'],
                                               universal_newlines=True).strip()

py2version = match('(?P<version>2\.\d\.\d)(?:.*)', sys.version)
