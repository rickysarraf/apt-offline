import os
import subprocess
from functools import partial

__all__ = ['resource_path', 'distribution_release']

resource_path = partial(os.path.join, os.path.dirname(__file__),
                        'resources')

distribution_release = subprocess.check_output(['lsb_release', '-r',
                                                '-s'],
                                               universal_newlines=True).strip()
