# A minor part of this code is taken from Nilton Volpato's progressbar implementation,
# precisely the terminal width probe code.
# Rest of the code was mostly from Dennis Lee Beiber
import signal, sys
from array import array

if sys.platform == "win32":
    pass
else:
    from fcntl import ioctl
    import termios


class ProgressBar(object):
    def __init__(self, minValue = 0, maxValue = 0, width = None, fd = sys.stderr):
        #width does NOT include the two places for [] markers
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
                self.width = 79 #The standard
        else:
            self.width = width
        self.value = self.min
        self.items = 0 #count of items being tracked
        self.complete = 0
        
    def handle_resize(self, signum, frame):
        h,w=array('h', ioctl(self.fd,termios.TIOCGWINSZ,'\0'*8))[:2]
        self.width = w
    
    def updateValue(self, newValue):
        #require caller to supply a value! newValue is the increment from last call
        self.value = max(self.min, min(self.max, self.value + newValue))
        self.display()
        
    def completed(self):
        self.complete = self.complete + 1
        if self.signal_set:
            signal.signal(signal.SIGWINCH, signal.SIG_DFL)
        self.display()
        
    def addItem(self, maxValue):
        self.max = self.max + maxValue
        self.span = float(self.max - self.min)
        self.items = self.items + 1
        self.display()
        
    def display(self):
        print "\r%3s/%3s items: %s\r" % (self.complete, self.items, str(self)),
        
    def __str__(self):
        #compute display fraction
        percentFilled = ((self.value - self.min) / self.span)
        widthFilled = int(self.width * percentFilled + 0.5)
        return ("[" + "#"*widthFilled + " "*(self.width - widthFilled) + "]" + " %5.1f%% of %d KB" % (percentFilled * 100.0, self.max/1024))
