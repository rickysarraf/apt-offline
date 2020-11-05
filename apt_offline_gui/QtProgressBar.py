class QtProgressBar( object ):

        def __init__( self, progressbar=None,label =None, minValue=0, maxValue=0, total_items=None):
            """
            Initialize progress bar

            Args:
                self: (todo): write your description
                progressbar: (bool): write your description
                label: (str): write your description
                minValue: (todo): write your description
                maxValue: (float): write your description
                total_items: (todo): write your description
            """
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
            """
            Resize signals.

            Args:
                self: (todo): write your description
                signum: (int): write your description
                frame: (todo): write your description
            """
                h, w = array( 'h', ioctl( self.fd, termios.TIOCGWINSZ, '\0' * 8 ) )[:2]
                self.width = w

        def updateValue( self, newValue ):
            """
            Updates the minimum value.

            Args:
                self: (todo): write your description
                newValue: (todo): write your description
            """
                #require caller to supply a value! newValue is the increment from last call
                self.value = max( self.min, min( self.max, self.value + newValue ) )
                self.display()

        def completed( self ):
            """
            Completed completion.

            Args:
                self: (todo): write your description
            """
                self.complete = self.complete + 1

                #if self.signal_set:
                        #signal.signal( signal.SIGWINCH, signal.SIG_DFL )
                self.display()

        def addItem( self, maxValue ):
            """
            Add a new item.

            Args:
                self: (todo): write your description
                maxValue: (int): write your description
            """
                self.max = self.max + maxValue
                self.span = float( self.max - self.min )
                if self.items_update is True:
                        self.items = self.items + 1
                self.display()

        def display( self ):
            """
            Display the progress bar.

            Args:
                self: (todo): write your description
            """
                #print "\r%3s /%3s items: %s\r" % ( self.complete, self.items, str( self ) ),
                self.progressBar.setValue(int(self.__str__()))
                progressText = "%3s /%3s  Size: %s" % ( self.complete, self.items, self.__numStr__( self.max / 1024 ))
                self.progressLabel.setText(progressText)

        def __str__( self ):
            """
            Return the percentage of the span.

            Args:
                self: (todo): write your description
            """
                #compute display fraction
                percentFilled = ( ( self.value - self.min ) / self.span )
                #widthFilled = int( self.width * percentFilled + 0.5 )
                #return ( "[" + "#"*widthFilled + " " * ( self.width - widthFilled ) + "]" + " %5.1f%% of %s" % ( percentFilled * 100.0, self.__numStr__( self.max / 1024 ) ) )
                return percentFilled

        def __numStr__( self, size ):
            """
            Return the number of bytes in a human - readable string.

            Args:
                self: (todo): write your description
                size: (int): write your description
            """
                if size > 1024:
                        size = size / 1024
                        if size > 1024:
                                size = size / 1024
                                return ( "%d GiB" % ( size ) )
                        return ( "%d MiB" % ( size ) )
                return ( "%d KiB" % ( size ) )
