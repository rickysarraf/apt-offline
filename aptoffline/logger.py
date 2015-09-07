from logging import getLogger, Formatter, DEBUG, INFO
from logutils.colorize import ColorizingStreamHandler


def initialize_logger(verbose):
    log = getLogger('apt-offline')
    h = ColorizingStreamHandler()
    formatter = Formatter("%(levelname)s: %(message)s")
    if verbose:
        log.setLevel(DEBUG)
        h.setLevel(DEBUG)
    else:
        log.setLevel(INFO)
        h.setLevel(INFO)
    h.setFormatter(formatter)
    log.addHandler(h)
