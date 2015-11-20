from logging import getLogger, Formatter, DEBUG, INFO
from .packages.logutils.colorize import ColorizingStreamHandler

#These are spaces which will overwrite the progressbar left mess
LINE_OVERWRITE_SMALL = " " * 10
LINE_OVERWRITE_MID = " " * 30
LINE_OVERWRITE_FULL = " " * 60

__all__ = ['LINE_OVERWRITE_FULL', 'LINE_OVERWRITE_MID',
           'LINE_OVERWRITE_SMALL', 'initialize_logger']


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
