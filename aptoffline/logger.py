import logging
from logutils.colorize import ColorizingStreamHandler


def initialize_logger(verbose):
    log = logging.getLogger('apt-offline')
    h = ColorizingStreamHandler()
    if verbose:
        h.setLevel(logging.DEBUG)
    else:
        h.setLevel(logging.INFO)
    log.addHandler(h)
