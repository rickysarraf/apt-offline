import sys
import signal
import array

try:
    from fcntl import ioctl
    import termios
except ImportError:
    pass


class ProgressBar(object):

        def __init__(self, minValue=0, maxValue=0, width=None,
                     total_items=None, fd=sys.stderr):
            # width does NOT include the two places for [] markers
            self.min = minValue
            self.max = maxValue
            self.span = float(self.max - self.min)
            self.fd = fd
            self.signal_set = False

            if width is None:
                try:
                    self.handle_resize(None, None)
                    signal.signal(signal.SIGWINCH, self.handle_resize)
                    self.signal_set = True
                except:
                    self.width = 79  # The standard

            else:
                self.width = width

            self.value = self.min

            if total_items is None or total_items <= 0:
                self.items = 0  # count of items being tracked
                self.items_update = True
            else:
                self.items = total_items
                self.items_update = False

            self.complete = 0

        def handle_resize(self, signum, frame):
            h, w = array('h', ioctl(self.fd, termios.TIOCGWINSZ,
                                    '\0' * 8))[:2]
            self.width = w

        def updateValue(self, newValue):
            # require caller to supply a value! newValue is the
            # increment from last call
            self.value = max(self.min,
                             min(self.max, self.value + newValue))
            self.display()

        def completed(self):
            self.complete = self.complete + 1

            if self.signal_set:
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)
                self.display()

        def addItem(self, maxValue):
            self.max = self.max + maxValue
            self.span = float(self.max - self.min)
            if self.items_update is True:
                self.items = self.items + 1
            self.display()

        def display(self):
            print("\r%3s / %3s items: {}\r".format(self.complete,
                                                   self.items,
                                                   self))

        def __str__(self):
            # compute display fraction
            percentFilled = (self.value - self.min) / self.span
            widthFilled = int(self.width * percentFilled + 0.5)
            return "[{}{}] %5.1f%% of %s".format("#"*widthFilled,
                                                 " "*(self.width -
                                                      widthFilled),
                                                 (percentFilled*100.0),
                                                 self.__numStr__(
                                                     self.max/1024))

        def __numStr__(self, size):
            if size > 1024:
                size = size / 1024
                if size > 1024:
                    size = size / 1024
                    return "%d GiB".format(size)
                return "%d MiB".format(size)
            return "%d KiB".format(size)
