from __future__ import absolute_import
import sys

try:
    from . import logutils
except ImportError:
    import logutils
    sys.modules['%s.logutils' % __name__] = logutils

try:
    from . import gnupg
except ImportError:
    import gnupg
    sys.modules['%s.gnupg' % __name__] = gnupg

try:
    from . import requests
except ImportError:
    import requests
    sys.modules['%s.requests' % __name__] = requests

if sys.version_info.major == 2:
    try:
        from . import concurrent
    except ImportError:
        import concurrent
        sys.modules['%s.requests' % __name__] = concurrent
