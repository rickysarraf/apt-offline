import logging
from logutils.colorize import ColorizingStreamHandler


def initialize_logger(verbose):
    log = logging.getLogger('apt-offline')
    h = ColorizingStreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    if verbose:
        log.setLevel(logging.DEBUG)
        h.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
        h.setLevel(logging.INFO)
    h.setFormatter(formatter)
    log.addHandler(h)
