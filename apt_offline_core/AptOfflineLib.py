
############################################################################
#    Copyright (C) 2005, 2015 Ritesh Raj Sarraf                            #
#    rrs@researchut.com                                                    #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import os
import sys

import threading

import zipfile
import bz2
import gzip

import errno
import shutil

import warnings


# LZMA is not native to Python in 2.x
modLZMA = True
try:
        import lzma
except ImportError:
        modLZMA = False
        sys.stderr.write("WARN: lzma module unavailable\n")
        sys.stderr.write("WARN: Please install Python lzma module for APT lzma backend\n")

WindowColor = True
try:
        import WConio
except ImportError:
        WindowColor = False


from array import array
import signal

#INFO: They aren't on Windows
try:
        from fcntl import ioctl
        import termios
except ImportError:
        pass


#INFO: Python 2.5 introduces hashlib.
# This module supports many hash/digest algorithms
# We do this check till Python 2.5 becomes widely used.
Python_2_5 = True
try:
        import hashlib
except ImportError:
        Python_2_5 = False


class Checksum:

    def HashMessageDigestAlgorithms( self, checksum, HashType, checksumFile ):

        try:
            data = open( checksumFile, 'rb' )
            if HashType == "sha256":
                Hash = self.sha256( data )
            elif HashType == "sha512":
                Hash = self.sha512( data )
            elif HashType == "md5" or HashType == "md5sum":
                Hash = self.md5( data )
            else: Hash = None
        except IOError:
            return False
        data.close()

        if Hash == checksum:
            return True
        return False

    def sha256( self, data ):
        sha256 = hashlib.sha256()
        sha256.update( data.read() )
        return sha256.hexdigest()

    def sha512( self, data ):
        sha512 = hashlib.sha512()
        sha512.update( data.read() )
        return sha512.hexdigest()

    def md5( self, data ):
        md5hash = hashlib.md5()
        md5hash.update( data.read() )
        return md5hash.hexdigest()

    def CheckHashDigest( self, checksumFile, checksum ):
        '''Return Bool against file and its checksum'''

        checksumType = checksum.split(":")[0]
        checksumType = checksumType.lower()
        checksum = checksum.split( ":" )[1]
        return self.HashMessageDigestAlgorithms( checksum, checksumType, checksumFile )


class Log:
        '''
        To display color on Windows CMD, we have optional dependency on WConio

        WConio can provide simple coloring mechanism for Microsoft Windows console
        Color Codes:
        Black = 0
        Green = 2
        Red = 4
        White = 15
        Light Red = 12
        Light Cyan = 11

        #FIXME: The Windows Command Interpreter does support colors natively. I think that support has been since Win2k.
        That's all for Windows Command Interpreter.

        As for ANSI Compliant Terminals (which most Linux/Unix Terminals are.).....
        I think the ANSI Color Codes would be good enough for my requirements to print colored text on an ANSI compliant terminal.

        The ANSI Terminal Specification gives programs the ability to change the text color or background color.
        An ansi code begins with the ESC character [^ (ascii 27) followed by a number (or 2 or more separated by a semicolon) and a letter.

        In the case of colour codes, the trailing letter is "m"...

        So as an example, we have ESC[31m ... this will change the foreground colour to red.

        The codes are as follows:

        For Foreground Colors
        1m - Hicolour (bold) mode
        4m - Underline (doesn't seem to work)
        5m - BLINK!!
        8m - Hidden (same colour as bg)
        30m - Black
        31m - Red
        32m - Green
        33m - Yellow
        34m - Blue
        35m - Magenta
        36m - Cyan
        37m - White

        For Background Colors

        40m - Change Background to Black
        41m - Red
        42m - Green
        43m - Yellow
        44m - Blue
        45m - Magenta
        46m - Cyan
        47m - White

        7m - Change to Black text on a White bg
        0m - Turn off all attributes.

        Now for example, say I wanted blinking, yellow text on a magenta background... I'd type ESC[45;33;5m
        '''

        def __init__( self, verbose, lock=None ):
                self.VERBOSE = bool( verbose )
                self.color_syntax = '\033[1;'

                if lock is True:
                        self.DispLock = threading.Lock()
                        self.lock = True
                else:
                        self.DispLock = False
                        self.lock = False

                if os.name == 'posix':
                        self.platform = 'posix'
                        self.color = {'Red': '31m', 'Black': '30m',
                                      'Green': '32m', 'Yellow': '33m',
                                      'Blue': '34m', 'Magenta': '35m',
                                      'Cyan': '36m', 'White': '37m',
                                      'Bold_Text': '1m', 'Underline': '4m',
                                      'Blink': '5m', 'SwitchOffAttributes': '0m'}

                elif os.name in ['nt', 'dos']:
                        self.platform = None

                        if WindowColor is True:
                                self.platform = 'microsoft'
                                self.color = {'Red': 4, 'Black': 0,
                                              'Green': 2, 'White': 15,
                                              'Cyan': 11, 'SwitchOffAttributes': 15}
                else:
                        self.platform = None
                        self.color = None

        def set_color( self, color ):
                '''Check the platform and set the color'''
                if self.platform == 'posix':
                        sys.stdout.write( self.color_syntax + self.color[color] )
                        sys.stderr.write( self.color_syntax + self.color[color] )
                elif self.platform == 'microsoft':
                        WConio.textcolor( self.color[color] )

        def msg( self, msg ):
                '''Print general messages. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire()

                #self.set_color( 'White' )
                sys.stdout.write( msg )
                sys.stdout.flush()
                #self.set_color( 'SwitchOffAttributes' )

                if self.lock:
                        self.DispLock.release()

        def warn( self, msg ):
                '''Print messages with a warning. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire()

                self.set_color( 'Magenta' )
                sys.stderr.write( "WARN: " + msg )
                sys.stderr.flush()
                self.set_color( 'SwitchOffAttributes' )

                if self.lock:
                        self.DispLock.release()

        def err( self, msg ):
                '''Print messages with an error. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire()

                self.set_color( 'Red' )
                sys.stderr.write( "ERROR: " + msg )
                sys.stderr.flush()
                self.set_color( 'SwitchOffAttributes' )

                if self.lock:
                        self.DispLock.release()

        def success( self, msg ):
                '''Print messages with a success. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire()

                self.set_color( 'Green' )
                sys.stdout.write( msg )
                sys.stdout.flush()
                self.set_color( 'SwitchOffAttributes' )

                if self.lock:
                        self.DispLock.release()

        # For the rest, we need to check the options also
        def verbose( self, msg ):
                '''Print verbose messages. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire()

                if self.VERBOSE is True:
                        self.set_color( 'Magenta' )
                        sys.stdout.write( "VERBOSE: " + msg )
                        sys.stdout.flush()
                        self.set_color( 'SwitchOffAttributes' )

                if self.lock:
                        self.DispLock.release()

        def calcSize( self, size ):
                ''' Takes number of kB and returns a string
                of proper size. Like if > 1024, return a megabyte '''
                if size > 1024:
                        size = size // 1024
                        if size > 1024:
                                size = size // 1024
                                return ( "%d GiB" % ( size ) )
                        return ( "%d MiB" % ( size ) )
                return ( "%d KiB" % ( size ) )


class ProgressBar( object ):

        def __init__( self, minValue=0, maxValue=0, width=None, total_items=None, fd=sys.stderr ):
                #width does NOT include the two places for [] markers
                self.min = minValue
                self.max = maxValue
                self.span = float( self.max - self.min )
                if self.span == 0:
                    self.span = 1
                self.fd = fd
                self.signal_set = False

                if width is None:
                        try:
                                self.handle_resize( None, None )
                                signal.signal( signal.SIGWINCH, self.handle_resize )
                                self.signal_set = True
                        except:
                                self.width = 79 #The standard

                else:
                        self.width = width

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

                if self.signal_set:
                        signal.signal( signal.SIGWINCH, signal.SIG_DFL )
                self.display()

        def addItem( self, maxValue ):
                self.max = self.max + maxValue
                self.span = float( self.max - self.min )
                if self.items_update is True:
                        self.items = self.items + 1
                self.display()

        def display( self ):
                sys.stdout.write("\r%3s / %3s items: %s\r" % ( self.complete, self.items, str( self ) ))

        def __str__( self ):
                #compute display fraction
                percentFilled = ( ( self.value - self.min ) / self.span )
                widthFilled = int( self.width * percentFilled + 0.5 )
                return ( "[" + "#"*widthFilled + " " * ( self.width - widthFilled ) + "]" + " %5.1f%% of %s" % ( percentFilled * 100.0, self.__numStr__( self.max / 1024 ) ) )

        def __numStr__( self, size ):
                if size > 1024:
                        size = size / 1024
                        if size > 1024:
                                size = size / 1024
                                return ( "%d GiB" % ( size ) )
                        return ( "%d MiB" % ( size ) )
                return ( "%d KiB" % ( size ) )


class AptOfflineErrors(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class AptOfflineLibShutilError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class Archiver:
        def __init__( self, lock=None ):
                if lock is None or lock != 1:
                        self.ZipLock = False
                else:
                        self.ZipLock = threading.Lock()
                        self.lock = True

                #INFO: Needed for bug reports in multiple threads. Because you can have multiple bug reports
                # for the same src package
                # https://github.com/rickysarraf/apt-offline/issues/44
                self.file_possibly_deleted = False

        def TarGzipBZ2_Uncompress( self, SourceFileHandle, TargetFileHandle ):
                try:
                        TargetFileHandle.write( SourceFileHandle.read() )
                except EOFError:
                        pass
                except IOError:
                        #TODO: What constitutes an "IOError: invalid data stream" ???
                        # Couldn't find much from the docs. Needs to be investigated.

                        # Answer:
                        # A BZ2 file corruption is seen during file creation only.
                        # Perhaps it has to do with the bad network, loss of packets et cetera
                        # The safest bet at the moment is to simply discard such files, which were
                        # downloaded in damaged form.
                        return False
                return True

        def compress_the_file( self, zip_file_name, files_to_compress ):
                '''Condenses all the files into one single file for easy transfer'''

                try:
                        if self.lock:
                                self.ZipLock.acquire( True )
                        filename = zipfile.ZipFile( zip_file_name, "a" )
                        fileOpened = True
                except IOError:
                        #INFO: By design zipfile throws an IOError exception when you open
                        # in "append" mode and the file is not present.

                        fileOpened = False
                        try:
                                filename = zipfile.ZipFile( zip_file_name, "w" )
                                fileOpened = True
                        except IOError:
                                fileOpened = False
                if fileOpened: #Supported from Python 2.5 ??

                        #INFO: We could get duplicate files being writted to the zip archive.
                        # See explanation below in the exception
                        warnings.filterwarnings('error')

                        try:
                                filename.write( files_to_compress, os.path.basename( files_to_compress ), zipfile.ZIP_DEFLATED )
                        except OSError as e:
                                if e.errno == errno.ENOENT:
                                        #INFO: We could be here, because in another thread (amd64), it completed, i.e. wrote to the archive and removed
                                        # And by the time this thread got a chance, the file was deleted by the previous thread
                                        #
                                        # A more ideal fix will be to check for files_to_compress's presence in zipfile at this stage
                                        self.file_possibly_deleted = True
                                        raise AptOfflineErrors("Ignoring err ENOENT, multiarch package name clash %s\n" % (files_to_compress))
                        except UserWarning as e:
                            raise AptOfflineErrors("Ignoring err type %s\n" % (e.args))
                        finally:
                            filename.close()
                            if self.lock:
                                self.ZipLock.release()
                        return True
                else:
                        if self.lock:
                                self.ZipLock.release()
                        return False

        def decompress_the_file( self, archive_file, target_file, archive_type ):
                '''Extracts all the files from a single condensed archive file'''
                if archive_type == "bzip2" or archive_type == "gzip" or archive_type == "xz":
                        if archive_type == "bzip2":
                                try:
                                        read_from = bz2.BZ2File( archive_file, 'r' )
                                except IOError:
                                        return False
                        elif archive_type == "gzip":
                                try:
                                        read_from = gzip.GzipFile( archive_file, 'r' )
                                except IOError:
                                        return False
                        elif archive_type == "xz":
                                if modLZMA is True:
                                        try:
                                                read_from = lzma.LZMAFile(archive_file, 'rb')
                                        except IOError:
                                                return False
                                else:
                                        return False
                        else:
                                return False

                        try:
                                write_to = open ( target_file, 'wb' )
                        except IOError:
                                return False

                        if self.TarGzipBZ2_Uncompress( read_from, write_to ) != True:
                                #INFO: Return False for the stream that failed.
                                return False
                        write_to.close()
                        read_from.close()
                        return True
                elif archive_type == "zip":
                        #INFO: We will never reach here.
                        # Package data from Debian is usually served only in bz2 or gzip format
                        # Plain zip is something we might never see.
                        # Leaving it here just like that. Maybe we will use it in the future

                        # FIXME: This looks odd. Where are we writing to a file ???
                        try:
                                zip_file = zipfile.ZipFile( archive_file, 'r' )
                        except IOError:
                                return False
                        #FIXME:
                        for filename in zip_file.namelist():
                                try:
                                        write_to = open ( filename, 'wb' )
                                except IOError:
                                        return False
                                write_to.write(zip_file.read(filename) )
                                write_to.flush()
                                write_to.close()
                        zip_file.close()
                        return True
                else:
                        return False

class FileMgmt( object ):

        def __init__( self ):
                self.duplicate_files = []

        def files( self, root ):
                for path, folders, files in os.walk( root ):
                        for f in files:
                                yield path, f

        def find_first_match( self, cache_dir=None, filename=None ):
                '''Return the full path of the filename if a match is found
                Else Return False'''

                if cache_dir is None:
                        return False
                elif filename is None:
                        return False
                elif os.path.isdir( cache_dir ) is False:
                        return False
                else:
                        for path, f in self.files( cache_dir ):
                                if f == filename:
                                        return os.path.join( path, f )
                        return False

        def rename_file( self, orig, new ):
                '''Rename file from orig to new'''
                if not os.path.isfile( orig ):
                        return False
                os.rename( orig, new )
                return True

        def remove_file( self, src ):
                '''Remvoe the given src file.'''
                try:
                        os.unlink( src )
                except IOError:
                        return False

        def move_file( self, src, dest ):
            '''Move file from src to dest.'''
            if not os.path.isdir( dest ):
                return False
            try:
                shutil.move(src, dest)
            except IOError:
                return False
            except:
                #INFO: These errors happen when, say, you have duplicate files
                # shutil didn't show a nice exception handle
                # So we propagate the failure and warn out loud in the caller
                raise AptOfflineLibShutilError("Possbile duplicate file %s already present in %s\n" % (src, dest))
            return True

        def copy_file(self, src, dest):
            '''Copy file from src to dest'''
            try:
                #INFO: If src and dest are the same, it is effectively opening the same file
                # in read and write modes, which leads to NULL data corruption
                destFile = os.path.join(dest, os.path.basename(src))
                srcFile = os.path.abspath(src)
                #print(srcFile, destFile)
                if srcFile == destFile:
                    return True
                SFH = open(srcFile, 'rb')
                DFH = open(destFile, 'wb')

                DFH.write(SFH.read())
                DFH.flush()
                DFH.close()
                SFH.close()
            except IOError:
                SFH.close()
                return False

        def move_folder( self, src, dest ):
                '''Move folder from src to dest.'''
                if os.path.isdir( dest ):
                        try:
                                os.rename( src, dest + "/" + os.path.basename( src ) )
                        except IOError:
                                return False

        def find_dup( self, dir ):
                '''"dir" will be the directory within which duplicate files are searched
                Returns a list with the duplicates'''

                #TODO: This is buggy currently

                for xpath, yfile in dir:

                        for path, file in dir:
                                if file == yfile:
                                        if not ( xpath + "/" + yfile == path + "/" + file ):
                                                if [xpath + "/" + yfile, path + "/" + file] in self.duplicate_files:
                                                        break
                                        else:
                                                self.duplicate_files += [ [xpath + "/" + yfile, path + "/" + file] ]
                                        #self.duplicate_files = set(self.duplicate_files)

                len = self.duplicate_files.__len__()
                print(len)
                for x in range( len ):
                        self.duplicate_files[x].sort()
                self.duplicate_files.sort()
                num = 0
                number = 0
                for ( x, y ) in self.duplicate_files:
                        while number < len - 1:
                                if x in self.duplicate_files[number] or y in self.duplicate_files[number]:
                                        num += 1
                                        print(num)
                                        if num > 1:
                                                print("Num went 2")
                                                self.duplicate_files.pop( number )
                                                num -= 0
                                number += 1

                return self.duplicate_files

class MyThread( threading.Thread ):
        """My thread class"""
        def __init__( self, WorkerFunction, requestQueue=None, responseQueue=None, NumOfThreads=1 ):
                # Pool of NUMTHREADS Threads that run run().
                self.requestQueue = requestQueue
                self.responseQueue = responseQueue
                self.threads = NumOfThreads
                self.threads_finished = 0   # used by gui to understand if things got over
                self.guiTerminateSignal=False
                self.WorkerFunction = WorkerFunction
                self.thread_pool = [
                       threading.Thread(
                              target=self.run,
                              args=()
                              )
                       for i in range( self.threads )
                       ]
                for thread in self.thread_pool:
                        thread.guiTerminateSignal=False

        def startThreads( self ):
                for thread in self.thread_pool:
                        thread.start()

        def stopThreads( self ):
                '''Shut down the threads after all requests end.
                (Put one None "sentinel" for each thread.)'''
                for thread in self.thread_pool:
                        self.requestQueue.put( None )

        def populateQueue( self, item ):
                self.requestQueue.put( item )

        def stopQueue( self, timeout=0 ):
                '''Don't end the program prematurely.
                (Note that because Queue.get() is blocking by
                default this isn't strictly necessary. But if
                you were, say, handling responses in another
                thread, you'd want something like this in your
                main thread.)'''
                if timeout !=0:
                        self.threads_finished = 0   # recount finished threads if gui handler needs
                for thread in self.thread_pool:
                        if timeout==0:
                                thread.join()
                        else:
                                # let threads also lookout for gui signals of cancellation
                                thread.join(timeout)
                                if not thread.is_alive():
                                        self.threads_finished += 1

        def run( self, item=None):
                while True:
                        if threading.current_thread().guiTerminateSignal:
                                break
                        if self.requestQueue is not None:
                                item = self.requestQueue.get()

                        if item is None:
                                break

                        thread_name = threading.current_thread().name

                        if self.responseQueue is not None:
                                self.responseQueue.put( self.WorkerFunction( item, thread_name ) )
                                exit_status = self.responseQueue.get()
                        else:
                                self.WorkerFunction( item, thread_name )

