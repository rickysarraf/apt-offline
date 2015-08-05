import os
from functools import partial

__all__ = ['resource_path']

resource_path = partial(os.path.join, os.path.dirname(__file__),
                                     'resources')
