class QtProgressBar( object ):

        def __init__( self, progressbar=None,label =None, minValue=0, maxValue=0, total_items=None):
                self.min = minValue
                self.max = maxValue
                self.span = float( self.max - self.min )
                self.fd = fd
                self.signal_set = False

                # This field stores QProgessBar
                self.progressBar = progressbar
                # This field stores the Label
                self.progressLabel = label

                self.value = self.min

                if total_items is None or total_items <= 0:
                        self.items = 0 #count of items being tracked
                        self.items_update = True
                else:
                        self.items = total_items
                        self.items_update = False

                self.complete = 0

        def handle_resize( self, signum, frame ):
                h, w = array( 'h', ioctl( self.fd, termios.TIOCGWINSZ, '\0' * 8 ) )[:2]
                self.width = w

        def updateValue( self, newValue ):
                #require caller to supply a value! newValue is the increment from last call
                self.value = max( self.min, min( self.max, self.value + newValue ) )
                self.display()

        def completed( self ):
                self.complete = self.complete + 1

                #if self.signal_set:
                        #signal.signal( signal.SIGWINCH, signal.SIG_DFL )
                self.display()

        def addItem( self, maxValue ):
                self.max = self.max + maxValue
                self.span = float( self.max - self.min )
                if self.items_update is True:
                        self.items = self.items + 1
                self.display()

        def display( self ):
                #print "\r%3s /%3s items: %s\r" % ( self.complete, self.items, str( self ) ),
                self.progressBar.setValue(int(self.__str__()))
                progressText = "%3s /%3s  Size: %s" % ( self.complete, self.items, self.__numStr__( self.max / 1024 ))
                self.progressLabel.setText(progressText)

        def __str__( self ):
                #compute display fraction
                percentFilled = ( ( self.value - self.min ) / self.span )
                #widthFilled = int( self.width * percentFilled + 0.5 )
                #return ( "[" + "#"*widthFilled + " " * ( self.width - widthFilled ) + "]" + " %5.1f%% of %s" % ( percentFilled * 100.0, self.__numStr__( self.max / 1024 ) ) )
                return percentFilled

        def __numStr__( self, size ):
                if size > 1024:
                        size = size / 1024
                        if size > 1024:
                                size = size / 1024
                                return ( "%d GiB" % ( size ) )
                        return ( "%d MiB" % ( size ) )
                return ( "%d KiB" % ( size ) )
