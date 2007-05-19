import os
import sys
import shutil
import platform
import string
import urllib2
import Queue
import threading
import signal
import optparse
import array

from array import array

#INFO: They aren't on Windows
try:
    from fcntl import ioctl
    import termios
except ImportError:
    pass

WindowColor = True
try:
    import WConio
except ImportError:
    WindowColor = False

'''This is the core module. It does the main job of downloading packages/update packages,\nfiguring out if the packages are in the local cache, handling exceptions and many more stuff'''


version = "0.7.0"
copyright = "(C) 2005 - 2007 Ritesh Raj Sarraf - RESEARCHUT (http://www.researchut.com/)"
        
errlist = []
supported_platforms = ["Linux", "GNU/kFreeBSD", "GNU"]
apt_update_target_path = '/var/lib/apt/lists/'
apt_package_target_path = '/var/cache/apt/archives/'
# Dummy paths while testing on Windows
#apt_update_target_path = 'C:\\temp'
#apt_package_target_path = 'C:\\temp'
       
       
class MD5Check:
    
    def md5_string(data):
        hash = md5.new()
        hash.update(data.read())
        return hash.hexdigest() 
    
    def md5_check(file, checksum):
        data = open(file, 'rb')
        #local = md5_string(data)
        if checksum == md5_string(data):
            return True
        return False
        
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
    
class Log:
    
    '''A OOP implementation for logging.
    warnings is to tackle the warning option
    verbose is to tackle the verbose option
    color is if you want to colorize your output
    
    You should pass these options, taking it from optparse/getopt,
    during instantiation'''
    
    ''' WConio can provide simple coloring mechanism for Microsoft Windows console
    Color Codes:
    Black = 0
    Green = 2
    Red = 4
    White = 15
    Light Red = 12
    Light Cyan = 11
    '''
    
    def __init__(self, warnings, verbose, color = None):
        
        if warnings is True:
            self.WARN = True
        else: self.WARN = False
        
        if verbose is True:
            self.VERBOSE = True
        else: self.VERBOSE = False
        
        self.color = color
        
    def msg(self, msg):
        'Print general messages'
        
        if self.color:
            WConio.textcolor(15)
            
        sys.stdout.write(msg)
        sys.stdout.flush()
        
    def err(self, msg):
        'Print messages with an error'
        
        if self.color:
            WConio.textcolor(4)
            
        sys.stderr.write(msg)
        sys.stderr.flush()
        
    def success(self, msg):
        'Print messages with a success'
        
        if self.color:
            WConio.textcolor(2)
            
        sys.stdout.write(msg)
        sys.stdout.flush()
    
    # For the rest, we need to check the options also
    def warn(self, msg):
        'Print warnings'
        
        if self.WARN is True:
            if self.color:
                WConio.textcolor(12)
                
            sys.stderr.write(msg)
            sys.stderr.flush()

    def verbose(self, msg):
        'Print verbose messages'
        
        if self.VERBOSE is True:
            if self.color:
                WConio.textcolor(11)
                
            sys.stdout.write(msg)
            sys.stdout.flush()
            
class Archiver:
    def __init__(self, lock=None):
        if lock is None or lock != 1:
            self.ziplock = False
        else:
            self.ZipLock = threading.Lock()
            self.lock = True
        
    def TarGzipBZ2_Uncompress(self, SourceFileHandle, TargetFileHandle):
        try:
            TargetFileHandle.write(SourceFileHandle.read() )
        except EOFError:
            pass
        return True
        
    def compress_the_file(self, zip_file_name, files_to_compress):
        '''Condenses all the files into one single file for easy transfer'''
        
        try:
            import zipfile
        except ImportError:
            return False
        
        try:
            if self.lock:
                self.ZipLock.acquire(True)
            filename = zipfile.ZipFile(zip_file_name, "a")
        except IOError:
            #INFO: By design zipfile throws an IOError exception when you open
            # in "append" mode and the file is not present.
            filename = zipfile.ZipFile(zip_file_name, "w")
        #except:
            #TODO Handle the exception
            #return False
        filename.write(files_to_compress, files_to_compress, zipfile.ZIP_DEFLATED)                        
        filename.close()
        
        if self.lock:
            self.ZipLock.release()
            
        return True
        
    def decompress_the_file(self, archive_file, path, target_file, archive_type):
        '''Extracts all the files from a single condensed archive file'''
        
        
        if archive_type is 1:
            try:
                import bz2
            except ImportError:
                return False
            
            try:
                read_from = bz2.BZ2File(archive_file, 'r')
            except:
                return False
                            
            try:
                write_to = open (os.path.join(path, filename), 'wb')
            except:
                return False
                            
            if TarGzipBZ2_Uncomprerssed(read_from, write_to) != True:
                raise ArchiveError
            write_to.close()
            read_from.close()
            return True
            
        elif archive_type is 2:
            try:
                import gzip
            except ImportError:
                return False
            
            try:
                read_from = gzip.GzipFile(file, 'r')
            except:
                return False
                            
            try:
                write_to = open(os.path.join(path,filename), 'wb')
            except:
                return False            
            
            if TarGzipBZ2_Uncomprerssed(read_from, write_to) != True:
                raise ArchiveError
            write_to.close()
            read_from.close()
            return True
            
        elif archive_type is 3:
            # FIXME: This looks odd. Where are we writing to a file ???
            try:
                zip_file = zipfile.ZipFile(file, 'rb')
            except:
                return False
                
            for filename in zip_file.namelist():
                data = zip_file.read()
            zip_file.close()
            return True
        
        else:
            return False


def FetchBugReportsDebian(PackageName, ZipFileName=None, lock=False):
    try:
        import debianbts
    except ImportError:
        return False
    
    bug_list = []
    bug_types = ["Resolved bugs", "Minor bugs", "Wishlist items"]
    #INFO: These are the ignore bug types. No one should really be caring about these
    
    
    if ZipFileName is not None:
        AddToArchive = Archiver(lock)
    
    (num_of_bugs, header, bugs_list) = debianbts.get_reports(PackageName)

    if num_of_bugs:
        for x in bugs_list:
            (sub_bugs_header, sub_bugs_list) = x
            
            for BugType in bug_types:
                if BugType in sub_bugs_header:
                    bug_flag = 0
                    break
                bug_flag = 1
                    
            if bug_flag:
                for x in sub_bugs_list:
                    break_bugs = x.split(':')
                    bug_num = string.lstrip(break_bugs[0], '#')
                    data = debianbts.get_report(bug_num, followups=True)
                    FileName = PackageName + "." + bug_num
                    file_handle = open(FileName, 'w')
                    file_handle.write(data[0] + "\n\n")
                    
                    for x in data[1]:
                        file_handle.write(x)
                        file_handle.write("\n")
                        
                    file_handle.write("\n" * 3)
                    file_handle.flush()
                    file_handle.close()
                    
                    if ZipFileName is not None:
                        AddToArchive.compress_the_file(ZipFileName, FileName)
                        os.unlink(FileName)
                        
        return True
    return False
    
    
def files(root): 
    for path, folders, files in os.walk(root): 
        for file in files: 
            yield path, file 
    
def find_first_match(cache_dir=None, filename=None):
    '''Return the full path of the filename if a match is found
    Else Return False'''

    # Do the sanity check first
    if cache_dir is None or filename is None or os.path.isdir(cache_dir) is False:
        return False
    else:
        for path, file in files(cache_dir): 
            if file == filename:
                return os.path.join(path, file)
            return False
            
class DownloadFromWeb(ProgressBar):
    
    def __init__(self, width):
        ProgressBar.__init__(self, width=width)
    
    def download_from_web(self, url, file, download_dir):
        '''
        Download the required file from the web
        The arguments are passed everytime to the function so that,
        may be in future, we could reuse this function
        '''
           
        try:
            block_size = 4096
            i = 0
            counter = 0
            
            os.chdir(download_dir)
            temp = urllib2.urlopen(url)
            headers = temp.info()
            size = int(headers['Content-Length'])
            data = open(file,'wb')
            
            #INFO: Add the download thread into the Global ProgressBar Thread
            self.addItem(size)
     
            while i < size:
                data.write (temp.read(block_size))
                increment = min(block_size, size - i)
                i += block_size
                counter += 1
                self.updateValue(increment)
                
            self.completed()
            data.close()
            temp.close()
            
            return True
            
        #FIXME: Find out optimal fix for this exception handling
        except OSError, (errno, strerror):
            #log.err("%s\n" %(download_dir))
            errfunc(errno, strerror, download_dir)
            
        except urllib2.HTTPError, errstring:
            #log.err("%s\n" % (file))
            errfunc(errstring.code, errstring.msg, file)
            
        except urllib2.URLError, errstring:
            #We pass error code "1" here becuase URLError
            # doesn't pass any error code.
            # URLErrors shouldn't be ignored, hence program termination
            if errstring.reason.args[0] == 10060:
                errfunc(errstring.reason.args[0], errstring.reason, url)
            #errfunc(1, errstring.reason)
            #pass
        
        except IOError, e:
            if hasattr(e, 'reason'):
                log.err("%s\n" % (e.reason))
            if hasattr(e, 'code') and hasattr(e, 'reason'):
                errfunc(e.code, e.reason, file)

def copy_first_match(cache_dir, filename, dest_dir, checksum): # aka new_walk_tree_copy() 
    '''Walks into "reposiotry" looking for "filename".
    If found, copies it to "dest_dir" but first verifies their md5 "checksum".'''
    
    # If the repository is not given, we'll return None because the user wants to download
    # it from the web
    # There's no need to walk also because the user knows that he doesn't have any cache_dir
    # Earlier implementation of having a default dir (os.curdir()) hit performance badly because
    # at times it would start the walk from "C:\" or "/"
    if cache_dir is None:
        return False
    
    for path, file in files(cache_dir): 
        if file == filename:
            #INFO: md5check is compulsory here
            # There's no point in checking for the disable-md5 option because
            # copying a damaged file is of no use
            if pypt_md5_check.md5_check(file, checksum, path) == True:
                try:
                    shutil.copy(os.path.join(path, file), dest_dir)
                except shutil.Error:
                    log.verbose("%s already available in dest_dir. Skipping copy!!!\n\n" % (file))
                return True
    return False

def stripper(item):
    '''Strips extra characters from "item".
    Breaks "item" into:
    url - The URL
    file - The actual package file
    size - The file size
    md5_text - The md5 checksum test
    and returns them.'''
    
    #INFO: This is obsolete
    #lSplitData = each_single_item.split(' ') # Split on the basis of ' ' i.e. space
    # We initialize the variables "sUrl" and "sFile" here.
    # We also strip the single quote character "'" to get the real data
    #sUrl = string.rstrip(string.lstrip(''.join(lSplitData[0]), chars="'"), chars="'")
    #sFile = string.rstrip(string.lstrip(''.join(lSplitData[1]), chars="'"), chars="'")
            
    item = item.split(' ')
    url = string.rstrip(string.lstrip(''.join(item[0]), chars="'"), chars="'")
    file = string.rstrip(string.lstrip(''.join(item[1]), chars="'"), chars="'")
    size = int(string.rstrip(string.lstrip(''.join(item[2]), chars = "'"), chars="'"))
    #INFO: md5 ends up having '\n' with it.
    # That needs to be stripped too.
    md5_text = string.rstrip(string.lstrip(''.join(item[3]), chars = "'"), chars = "'")
    md5_text = string.rstrip(md5_text, chars = "\n")
    
    return url, file, size, md5_text


def errfunc(errno, errormsg, filename):
    '''
    We use errfunc to handler errors.
    There are some error codes (-3 and 13 as of now)
    which are temporary codes, they happen when there
    is a temporary resolution failure, for example.
    For such situations, we can't abort because the
    uri file might have other hosts also, which might
    be well accessible.
    This function does the job of behaving accordingly
    as per the error codes.
    '''
    error_codes = [-3, 13, 504, 404, 10060, 104]
    # 104, 'Connection reset by peer'
    # 504 is for gateway timeout
    # 404 is for URL error. Page not found.
    # 10060 is for Operation Time out. There can be multiple reasons for this timeout
    
    #TODO: Find out what these error codes are for
    # and better document them the next time you find it out.
    # 13 is for "Permission Denied" when you don't have privileges to access the destination 
    if errno in error_codes:
        log.err("%s - %s - %s\n" % (filename, errno, errormsg))
        log.verbose(" Will still try with other package uris\n\n")
        pass
    
    elif errno == 407 or errno == 2:
        # These, I believe are from OSError/IOError exception.
        # I'll document it as soon as I confirm it.
        log.err("%s\n" % (errormsg))
        sys.exit(errno)
        
    elif errno == 1:
        log.err(errormsg)
        log.err("Explicit program termination %s\n" % (errno))
        sys.exit(errno)
        
    else:
        log.err("Aieee! I don't understand this errorcode\n" % (errno))
        sys.exit(errno)
    
def fetcher(ArgumentOptions, arg_type = None):
    '''
    uri - The uri data whill will contain the information
    path - The path (if any) where the download needs to be done
    cache - The cache (if any) where we should check before downloading from the net
    arg_type - arg_type is basically used to identify wether it's a update download or upgrade download
    '''
    
    cache_dir = ArgumentOptions.cache_dir
    
    class FetcherClass(DownloadFromWeb, Archiver, MD5Check):
        def __init__(self, width, lock):
            DownloadFromWeb.__init__(self, width=width)
            #ProgressBar.__init__(self, width)
            #self.width = width
            Archiver.__init__(self, lock=lock)
            #self.lock = lock
            
    #global FetcherInstance
    FetcherInstance = FetcherClass(width=30, lock=True)
    #INFO: For the Progress Bar
    #progbar = ProgressBar(width = 30)
    
    if ArgumentOptions.download_dir is None:
        if os.access("pypt-downloads", os.W_OK) is True:
            download_path = os.path.abspath("pypt-downloads")
        else:
            try:
                os.umask(0002)
                os.mkdir("pypt-downloads")
                download_path = os.path.abspath("pypt-downloads")
            except:
                log.err("Aieeee! I couldn't create a directory")
                errfunc(1, '')
    else:
            download_path = os.path.abspath(ArgumentOptions.download_dir)
    
    FetchData = {}
    if ArgumentOptions.fetch_update:
        try:
           raw_data_list = open(ArgumentOptions.fetch_update, 'r').readlines()
        except IOError, (errno, strerror):
            log.err("%s %s\n" % (errno, strerror))
            errfunc(errno, '')
        
        FetchData['Update'] = []
        for item in raw_data_list:
            FetchData['Update'].append(item)
            
        if os.access(os.path.join(download_path, ArgumentOptions.zip_update_file), os.F_OK):
            log.err("%s already present.\nRemove it first.\n" % (ArgumentOptions.zip_update_file) )
            sys.exit(1)
        
            
    if ArgumentOptions.fetch_upgrade:
        try:
           raw_data_list = open(ArgumentOptions.fetch_upgrade, 'r').readlines()
        except IOError, (errno, strerror):
            log.err("%s %s\n" % (errno, strerror))
            errfunc(errno, '')
        
        FetchData['Upgrade'] = []
        for item in raw_data_list:
            FetchData['Upgrade'].append(item)
            
        if os.access(os.path.join(download_path, ArgumentOptions.zip_upgrade_file), os.F_OK):
            log.err("%s already present.\nRemove it first.\n" % (ArgumentOptions.zip_upgrade_file) )
            sys.exit(1)
            
    del raw_data_list
        
        
    #INFO: Mac OS is having issues with Python Threading.
    # Use the conventional model for Mac OS
    if sys.platform == 'darwin':
        log.verbose("Running on Mac OS! pypt-offline doesn't have proper support for Threads on Mac OS X.\n")
        log.verbose("Running in the conventional non-threaded way.\n")
        
        for key in FetchData.keys():
            for item in FetchData.get(key):
                
                (url, file, download_size, checksum) = stripper(each_single_item)
                
                if key == 'Update':
                    temp_file = file.split("_")
                    PackageName = temp_file[0]
                    PackageName += " - " + temp_file[len(temp_file) - 1]
                    del temp_file
                    
                    log.msg("Downloading %s\n" % (PackageName) ) 
                    if FetcherInstance.download_from_web(url, file, download_path) != True:
                        errlist.append(file)
                    else:
                        log.success("\n%s done.\n" % (PackageName) )
                        if ArgumentOptions.zip_it:
                            if FetcherInstance.compress_the_file(ArgumentOptions.zip_update_file, file) != True:
                                log.verbose("%s added to archive %s.\n" % (file, ArgumentOptions.zip_update_file) )
                                os.unlink(os.path.join(download_path, file) ) # Remove it because we don't need the file once it is zipped.
                                #sys.exit(1)
                        pass
                                        
                elif key == 'Upgrade':
                    PackageName = file.split("_")[0]
                    if cache_dir is None:
                        log.msg("Downloading %s - %d KB\n" % (file, size/1024))
                        
                        if FetcherInstance.download_from_web(url, file, download_path) != True:
                            errlist.append(PackageName)
                            
                            bug_report_fetch_flag = 0
                            if ArgumentOptions.zip_it:
                                log.success("\n%s done.\n" % (PackageName) )
                                FetcherInstance.compress_the_file(ArgumentOptions.zip_upgrade_file, file)
                                os.unlink(os.path.join(download_path, file))
                                if ArgumentOptions.deb_bugs:
                                    if FetchBugReportsDebian(PackageName, ArgumentOptions.zip_upgrade_file) is True:
                                        log.verbose("Fetched bug reports for package %s and archived to file %s.\n" % (PackageName, ArgumentOptions.zip_upgrade_file) )
                                        bug_report_fetch_flag = 1
                                    
                            if ArgumentOptions.deb_bugs and bug_report_fetch_flag != 1:
                                if FetchBugReportsDebian(PackageName) is True:
                                    log.verbose("Fetched bug reports for package %s.\n" % (PackageName) )
                    else:
                        if find_first_match(cache_dir, file, download_path, checksum) == False:
                            log.msg("Downloading %s - %d KB\n" % (PackageName, size/1024))
                            
                            if FetcherInstance.download_from_web(url, file, download_path) != True:
                                 errlist.append(PackageName)
                            else:
                                log.success("\n%s done.\n" % (PackageName) )
                                if os.access(os.path.join(cache_dir, file), os.F_OK):
                                    log.verbose("%s file is already present in cache-dir %s. Skipping copy.\n" % (file, cache_dir) ) #INFO: The file is already there.
                                else:
                                    if os.access(cache_dir, os.W_OK):
                                        shutil.copy(file, cache_dir)
                                        log.verbose("%s copied to %s\n" % (file, cache_dir))
                                    else:
                                        log.verbose("Cannot copy %s to %s. Is %s writeable??\n" % (file, cache_dir))
                                        
                                bug_report_fetch_flag = 0
                                if ArgumentOptions.zip_it:
                                    FetcherInstance.compress_the_file(ArgumentOptions.zip_upgrade_file, file)
                                    os.unlink(os.path.join(download_path, file))
                                    if ArgumentOptions.deb_bugs:
                                        FetchBugReportsDebian(PackageName, ArgumentOptions.zip_upgrade_file)
                                        log.verbose("Fetched bug reports for package %s and archived to file %s.\n" % (PackageName, ArgumentOptions.zip_upgrade_file) )
                                        bug_report_fetch_flag = 1
                                        
                                if ArgumentOptions.deb_bugs and bug_report_fetch_flag != 1:
                                    if FetchBugReportsDebian(PackageName) is True:
                                        log.verbose("Fetched bug reports for package %s.\n" % (PackageName) )
                        elif True:
                            bug_report_fetch_flag = 0
                            if ArgumentOptions.zip_it:
                                FetcherInstance.compress_the_file(ArgumentOptions.zip_upgrade_file, file)
                                os.unlink(os.path.join(download_path, file))
                                if ArgumentOptions.deb_bugs:
                                    if FetchBugReportsDebian(PackageName, ArgumentOptions.zip_upgrade_file) is True:
                                        log.verbose("Fetched bug reports for package %s and archived to file %s.\n" % (PackageName, ArgumentOptions.zip_upgrade_file) )
                                        bug_report_fetch_flag = 1
                                    
                            if ArgumentOptions.deb_bugs and bug_report_fetch_flag != 1:
                                if FetchBugReportsDebian(PackageName) is True:
                                    log.verbose("Fetched bug reports for package %s.\n" % (PackageName) )
                else:
                    raise FetchDataKeyError
                    
    else:
        #INFO: Thread Support
        if ArgumentOptions.num_of_threads > 1:
            log.msg("WARNING: Threads is still in beta stage. It's better to use just a single thread at the moment.\n\n")
            
        def run(request, response, func=find_first_match):
            '''Get items from the request Queue, process them
            with func(), put the results along with the
            Thread's name into the response Queue.
            
            Stop running when item is None.'''
        
            while 1:
                tuple_item_key = request.get()
                if tuple_item_key is None:
                    break
                (key, item) = tuple_item_key
                (url, file, download_size, checksum) = stripper(item)
                thread_name = threading.currentThread().getName()
                
                if key == 'Update':
                    temp_file = file.split("_")
                    PackageName = temp_file[0]
                    PackageName += " - " + temp_file[len(temp_file) - 1]
                    del temp_file
                    
                    #INFO: We pass None as a filename here because we don't want to do a tree search of
                    # update files. Update files are changed daily and there is no point in doing a search of
                    # them in the cache_dir
                    response.put(func(cache_dir, None) )
                    
                    #INFO: exit_status here would be False because for updates there's no need to do a
                    # find_first_match
                    # This is more with the above statement where None is passed as the filename
                    exit_status = response.get()
                    
                    if exit_status == False:
                        log.msg("Downloading %s\n" % (PackageName) ) 
                        
                        if FetcherInstance.download_from_web(url, file, download_path) == True:
                            log.success("\r%s done.%s\n" % (PackageName, " "* 60) )
                            if ArgumentOptions.zip_it:
                                if FetcherInstance.compress_the_file(ArgumentOptions.zip_update_file, file) != True:
                                    log.err("Couldn't archive %s to file %s.\n" % (file, ArgumentOptions.zip_update_file) )
                                    sys.exit(1)
                                os.unlink(os.path.join(download_path, file) )
                        else:
                            errlist.append(file)
                                
                elif key == 'Upgrade':
                    PackageName = file.split("_")[0]
                    response.put(func(cache_dir, file) ) 
                    #INFO: find_first_match() returns False of a file name with absolute path
                    full_file_path = response.get()
                    
                    if full_file_path != False:
                        if ArgumentOptions.disable_md5check is False:
                            if FetcherInstance.md5_check(full_file_path, checksum) is True:
                                if ArgumentOptions.zip_it:
                                    if FetcherInstance.compress_the_file(ArgumentOptions.zip_upgrade_file, full_file_path) is True:
                                        log.success("%s copied from local cache directory %s\n" % (PackageName, cache_dir) )
                                        if ArgumentOptions.deb_bugs:
                                            if FetchBugReportsDebian(PackageName, ArgumentOptions.zip_upgrade_file, lock=True) is True:
                                                log.verbose("Fetched bug reports for package %s and archived to file %s.\n" % (PackageName, ArgumentOptions.zip_upgrade_file) )
                                else:
                                    try:
                                        shutil.copy(full_file_path, download_path)
                                        log.success("%s copied from local cache directory %s\n" % (PackageName, cache_dir) )
                                    except shutil.Error:
                                        log.verbose("%s already available in %s. Skipping copy!!!\n\n" % (file, download_path) )
                                                
                                    if ArgumentOptions.deb_bugs:
                                        if FetchBugReportsDebian(PackageName, lock=True) is True:
                                            log.verbose("Fetched bug reports for package %s.\n" % (PackageName) )
                                        
                            else:
                                log.verbose("%s MD5 checksum mismatch. Skipping file.\n" % (file) )
                                log.msg("Downloading %s - %d KB\n" % (PackageName, download_size/1024) )
                                if FetcherInstance.download_from_web(url, file, download_path) == True:
                                    log.success("\r%s done.%s\n" % (PackageName, " "* 60) )
                                    if ArgumentOptions.cache_dir:
                                        try:
                                            shutil.copy(file, cache_dir)
                                            log.verbose("%s copied to local cache directory %s\n" % (file, ArgumentOptions.cache_dir) )
                                        except shutil.Error:
                                            log.verbose("Couldn't copy %s  to %s\n\n" % (file, ArgumentOptions.cache_dir) )
                                    if ArgumentOptions.zip_it:
                                        if FetcherInstance.compress_the_file(ArgumentOptions.zip_upgrade_file, file) != True:
                                            log.err("Couldn't archive %s to file %s\n" % (file, ArgumentOptions.zip_upgrade_file) )
                                            sys.exit(1)
                                        os.unlink(os.path.join(download_path, file) )
                                        bug_report_fetch_flag = 0
                                        if ArgumentOptions.deb_bugs:
                                            if FetchBugReportsDebian(PackageName, ArgumentOptions.zip_upgrade_file, lock=True) is True:
                                                log.verbose("Fetched bug reports for package %s and archived to file %s.\n" % (PackageName, ArgumentOptions.zip_upgrade_file) )
                                                bug_report_fetch_flag = 1
                                                
                                    if ArgumentOptions.deb_bugs and bug_report_fetch_flag != 1:
                                        if FetchBugReportsDebian(PackageName, lock=True) is True:
                                            log.verbose("Fetched bug reports for package %s.\n" % (PackageName) )
                                        
                        else:
                            #INFO: If md5check is disabled, just copy it to the cache_dir
                            try:
                                shutil.copy(full_file_path, download_path)
                                log.success("%s copied from local cache directory %s\n" % (file, cache_dir) )
                            except shutil.Error:
                                log.verbose("%s already available in dest_dir. Skipping copy!!!\n\n" % (file) )
                    else:
                        log.verbose("%s not available in local cache %s.\n" % (file, ArgumentOptions.cache_dir) )
                        log.msg("Downloading %s - %d KB\n" % (PackageName, download_size/1024) )
                        if FetcherInstance.download_from_web(url, file, download_path) == True:
                            if ArgumentOptions.disable_md5check is False:
                                if FetcherInstance.md5_check(full_file_path, checksum) is True:
                                            
                                    if ArgumentOptions.cache_dir:
                                        try:
                                            shutil.copy(file, ArgumentOptions.cache_dir)
                                            log.verbose("%s copied to local cache directory %s\n" % (file, ArgumentOptions.cache_dir) )
                                        except shutil.Error:
                                            log.verbose("%s already available in %s. Skipping copy!!!\n\n" % (file, ArgumentOptions.cache_dir) )
                                            
                                    if ArgumentOptions.zip_it:
                                        if FetcherInstance.compress_the_file(ArgumentOptions.zip_upgrade_file, file) != True:
                                            log.err("Couldn't archive %s to file %s\n" % (file, ArgumentOptions.zip_upgrade_file) )
                                            sys.exit(1)
                                        log.verbose("%s added to archive %s\n" % (file, ArgumentOptions.zip_upgrade_file) )
                                        os.unlink(os.path.join(download_path, file) )
                                        bug_report_fetch_flag = 0
                                        if ArgumentOptions.deb_bugs:
                                            if FetchBugReportsDebian(PackageName, ArgumentOptions.zip_upgrade_file, lock=True) is True:
                                                log.verbose("Fetched bug reports for package %s and archived to file %s.\n" % (PackageName, ArgumentOptions.zip_upgrade_file) )
                                                bug_report_fetch_flag = 1
                                    if ArgumentOptions.deb_bugs:
                                        if FetchBugReportsDebian(PackageName, lock=True) is True:
                                            log.verbose("Fetched bug reports for package %s.\n" % (PackageName) )
                                            
                            if ArgumentOptions.zip_it:
                                if FetcherInstance.compress_the_file(ArgumentOptions.zip_upgrade_file, file) != True:
                                    log.err("Couldn't archive %s to file %s\n" % (file, ArgumentOptions.zip_upgrade_file) )
                                    sys.exit(1)
                                log.verbose("%s added to archive %s\n" % (file, ArgumentOptions.zip_upgrade_file) )
                                os.unlink(os.path.join(download_path, file) )
                                bug_report_fetch_flag = 0
                                if ArgumentOptions.deb_bugs:
                                    if FetchBugReportsDebian(PackageName, ArgumentOptions.zip_upgrade_file, lock=True) is True:
                                        log.verbose("Fetched bug reports for package %s and archived to file %s.\n" % (PackageName, ArgumentOptions.zip_upgrade_file) )
                                        bug_report_fetch_flag = 1
                                        
                            if ArgumentOptions.deb_bugs and bug_report_fetch_flag != 1:
                                if FetchBugReportsDebian(PackageName, lock=True) is True:
                                    log.verbose("Fetched bug reports for package %s.\n" % (PackageName) )
                                    
                            log.success("\r%s done.%s\n" % (PackageName, " "* 60) )
                        else:
                            #log.err("Couldn't find %s\n" % (PackageName) )
                            errlist.append(PackageName)
                    
        # Create two Queues for the requests and responses
        requestQueue = Queue.Queue()
        responseQueue = Queue.Queue()
        
        # Pool of NUMTHREADS Threads that run run().
        thread_pool = [
                       threading.Thread(
                              target=run,
                              args=(requestQueue, responseQueue)
                              )
                       for i in range(ArgumentOptions.num_of_threads)
                       ]
        
        # Start the threads.
        for t in thread_pool: t.start()
        
        # Queue up the requests.
        #for item in raw_data_list: requestQueue.put(item)
        for key in FetchData.keys():
            for item in FetchData.get(key):
                requestQueue.put( (key, item) )
        
        # Shut down the threads after all requests end.
        # (Put one None "sentinel" for each thread.)
        for t in thread_pool: requestQueue.put(None)
        
        # Don't end the program prematurely.
        #
        # (Note that because Queue.get() is blocking by
        # defualt this isn't strictly necessary. But if
        # you were, say, handling responses in another
        # thread, you'd want something like this in your
        # main thread.)
        for t in thread_pool: t.join()
                        
    # Print the failed files
    if len(errlist) == 0:
        log.msg("\nAll files have been downloaded.\n")
    else:
        log.err("\n\nThe following files failed to be downloaded.\n")
        for error in errlist:
            log.err("%s failed.\n" % (error))
        
def syncer(install_file_path, target_path, arg_type=None):
    '''Syncer does the work of syncing the downloaded files.
    It syncs "install_file_path" which could be a valid file path
    or a zip archive to "target_path'''
    
    archive = Archiver()
    if arg_type == 1:
        try:
            import zipfile
        except ImportError:
            log.err("Aieeee! Module zipfile not found.\n")
            sys.exit(1)
            
        try:
            import pypt_magic
        except ImportError:
            log.err("Aieeee! Module pypt_magic not found.\n")
            sys.exit(1)
            
        file = zipfile.ZipFile(install_file_path, "r")
        for filename in file.namelist():
                
            data = open(filename, "wb")
            data.write(file.read(filename))
            data.close()
            
            #FIXME: Fix this tempfile feature
            # Access to the temporary file is not being allowed
            # It's throwing a Permission denied exception
            #try:
            #    import tempfile
            #except ImportError:
            #    sys.stderr.write("Aieeee! Module pypt_magic not found.\n")
            #    sys.exit(1)
            #data = tempfile.NamedTemporaryFile('wb', -1, '', '', os.curdir)
            #data.write(file.read(filename))
            #data = file.read(filename)
            
            # retval = subprocess.call(['less', filename])
            
            if pypt_magic.file(os.path.abspath(filename)) == "application/x-bzip2":
                archive.decompress_the_file(os.path.abspath(filename), target_path, filename, 1)
            elif pypt_magic.file(os.path.abspath(filename)) == "application/x-gzip":
                archive.decompress_the_file(os.path.abspath(filename), target_path, filename, 2)
            elif pypt_magic.file(filename) == "PGP armored data" or pypt_magic.file(filename) == "application/x-dpkg":
                if os.access(target_path, os.W_OK):
                    shutil.copy(filename, target_path)
                    log.msg("%s file synced.\n" % (filename))
            os.unlink(filename)
                
    elif arg_type == 2:
        for eachfile in os.listdir(install_file_path):
            
            archive_file_types = ['application/x-bzip2', 'application/gzip', 'application/zip']
            archive_type = None
            try:
                import pypt_magic
            except ImportError:
                log.err("Aieeee! module not found.\n")
                
            if pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/x-bzip2":
                archive.decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 1)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/gzip":
                archive.decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 2)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/zip":
                archive.decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 3)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "PGP armored data" or pypt_magic.file(filename) == "application/x-dpkg":
                if os.access(target_path, os.W_OK):
                    shutil.copy(os.path.join(install_file_path, eachfile), target_path)
                    log.msg("%s file synced.\n" % (eachfile))
            else:
                log.err("Aieeee! I don't understand filetype %s\n" % (eachfile))
                
def main():
    '''Here we basically do the sanity checks, some validations
    and then accordingly call the corresponding functions.'''
    
    """Contains most of the variables that are required by the application to run.
    Also does command-line option parsing and variable validation."""
    
    parser = optparse.OptionParser(usage="%prog [OPTION1, OPTION2, ...]",
                                   version="%prog " + version + "\n" + copyright)
       
    parser.add_option("-d","--download-dir", dest="download_dir",
                      help="Root directory path to save the downloaded files", action="store", type="string", metavar="pypt-downloads")
    parser.add_option("-s","--cache-dir", dest="cache_dir",
                      help="Root directory path where the pre-downloaded files will be searched. If not, give a period '.'",
                      action="store", type="string", metavar=".")
    parser.add_option("--verbose", dest="verbose", help="Enable verbose messages", action="store_true")
    parser.add_option("--warnings", dest="warnings", help="Enable warnings", action="store_true")
    parser.add_option("-u","--uris", dest="uris_file",
                      help="Full path of the uris file which contains the main database of files to be downloaded",action="store", type="string")
    parser.add_option("","--disable-md5check", dest="disable_md5check",
                      help="Disable md5checksum validation on downloaded files",action="store_true")
    parser.add_option("", "--threads", dest="num_of_threads", help="Number of threads to spawn",
                      action="store", type="int", metavar="1", default=1)
       
    #INFO: Option zip is not enabled by default but is highly encouraged.
    parser.add_option("-z","--zip", dest="zip_it", help="Zip the downloaded files to a single zip file", action="store_true")
    parser.add_option("--zip-update-file", dest="zip_update_file", help="Default zip file for downloaded (update) data",
                      action="store", type="string", metavar="pypt-offline-update.zip", default="pypt-offline-update.zip")
    parser.add_option("--zip-upgrade-file", dest="zip_upgrade_file", help="Default zip file for downloaded (upgrade) data",
                      action="store", type="string", metavar="pypt-offline-upgrade.zip", default="pypt-offline-upgrade.zip")
       
    #INFO: At the moment nargs cannot be set to something like * so that optparse could manipulate n number of args. This is a limitation in optparse at the moment. The author might add this feature in the future.
    # When fixed by the author, we'd be in a better shape to use the above mentioned line instead of relying on this improper way.
    # With action="store_true", we are able to store all the arguments into the args variable from where it can be fetched later.
    #parser.add_option("", "--set-install-packages", dest="set_install_packages", help="Extract the list of uris which need to be fetched for installation of the given package and its dependencies", action="store", type="string", nargs=10, metavar="package_name")
    parser.add_option("", "--set-install", dest="set_install",
                      help="Extract the list of uris which need to be fetched for installation of the given package and its dependencies",
                      action="store", metavar="pypt-offline-install.dat")
    parser.add_option("", "--set-install-packages", dest="set_install_packages", help="Name of the packages which need to be fetched",
                      action="store_true", metavar="package_names")
       
    parser.add_option("", "--set-update", dest="set_update", help="Extract the list of uris which need to be fetched for updation",
                      action="store", type="string", metavar="pypt-offline-update.dat")
    parser.add_option("", "--fetch-update", dest="fetch_update",
                      help="Fetch the list of uris which are needed for apt's databases _updation_. This command must be executed on the WITHNET machine",
                      action="store", type="string", metavar="pypt-offline-update.dat")
    parser.add_option("", "--install-update", dest="install_update",
                      help="Install the fetched database files to the  NONET machine and _update_ the apt database on the NONET machine. This command must be executed on the NONET machine",
                      action="store", type="string", metavar="pypt-offline-update.zip")
    parser.add_option("", "--set-upgrade", dest="set_upgrade", help="Extract the list of uris which need to be fetched for _upgradation_",
                      action="store", type="string", metavar="pypt-offline-upgrade.dat")
    parser.add_option("", "--upgrade-type", dest="upgrade_type",
                      help="Type of upgrade to do. Use one of upgrade, dist-upgrade, dselect-ugprade",
                      action="store", type="string", metavar="upgrade")
    parser.add_option("", "--fetch-upgrade", dest="fetch_upgrade",
                      help="Fetch the list of uris which are needed for apt's databases _upgradation_. This command must be executed on the WITHNET machine",
                      action="store", type="string", metavar="pypt-offline-upgrade.dat")
    parser.add_option("", "--install-upgrade", dest="install_upgrade",
                      help="Install the fetched packages to the  NONET machine and _upgrade_ the packages on the NONET machine. This command must be executed on the NONET machine",
                      action="store", type="string", metavar="pypt-offline-upgrade.zip")
    parser.add_option("", "--fetch-bug-reports", dest="deb_bugs",
                      help="Fetch bug reports from the BTS", action="store_true")
    #global options, args
    (options, args) = parser.parse_args()
    
    try:
        # The log implementation
        # Instantiate the class
        global log
        log = Log(options.warnings, options.verbose, WindowColor)
        
        log.msg("pypt-offline %s\n" % (version))
        log.msg("Copyright %s\n" % (copyright))
        
        if options.set_update:
            if platform.system() in supported_platforms:
                if os.geteuid() != 0:
                    parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                else:
                    log.msg("Generating database of files that are needed for an update.\n")
                    os.environ['__pypt_set_update'] = options.set_update
                    if os.system('/usr/bin/apt-get -qq --print-uris update > $__pypt_set_update') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
            else:
                 parser.error("This argument is supported only on Unix like systems with apt installed\n")
            sys.exit(0)
     
        if options.set_upgrade or options.upgrade_type:
            if not (options.set_upgrade and options.upgrade_type):
                parser.error("Options --set-upgrade and --upgrade-type are mutually inclusive\n")
                     
            if platform.system() in supported_platforms:
                if os.geteuid() != 0:
                    parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                #TODO: Use a more Pythonic way for it
                if options.upgrade_type == "upgrade":
                    log.msg("Generating database of files that are needed for an upgrade.\n")
                    os.environ['__pypt_set_upgrade'] = options.set_upgrade
                    if os.system('/usr/bin/apt-get -qq --print-uris upgrade > $__pypt_set_upgrade') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
                elif options.upgrade_type == "dist-upgrade":
                    log.msg("Generating database of files that are needed for a dist-upgrade.\n")
                    os.environ['__pypt_set_upgrade'] = options.set_upgrade
                    if os.system('/usr/bin/apt-get -qq --print-uris dist-upgrade > $__pypt_set_upgrade') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
                elif options.upgrade_type == "dselect-upgrade":
                    log.msg("Generating database of files that are needed for a dselect-upgrade.\n")
                    os.environ['__pypt_set_upgrade'] = options.set_upgrade
                    if os.system('/usr/bin/apt-get -qq --print-uris dselect-upgrade > $__pypt_set_upgrade') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
                else:
                    parser.error("Invalid upgrade argument type selected\nPlease use one of, upgrade/dist-upgrade/dselect-upgrade\n")
            else:
                parser.error("This argument is supported only on Unix like systems with apt installed\n")
                sys.exit(0)
                 
        if options.set_install_packages or options.set_install:
            if not (options.set_install_packages and options.set_install):
                parser.error("Options --set-install and --set-install-package are mutually inclusive\n")
                
            if platform.system() in supported_platforms:
                if os.geteuid() != 0:
                    parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                    
                log.msg("Generating database of the package and its dependencies.\n")
                os.environ['__pypt_set_install'] = options.set_install
                os.environ['__pypt_set_install_packages'] = ''
                
                #INFO: This is improper way of getting the args, the name of the packages.
                # But since optparse doesn't have the implementation in place at the moment, we're using it.
                # Once fixed, this will be changed.
                # For details look at the parser.add_option line above.
                for x in args:
                    os.environ['__pypt_set_install_packages'] += x + ' '
                    
                #FIXME: Find a more Pythonic implementation
                if os.system('/usr/bin/apt-get -qq --print-uris install $__pypt_set_install_packages > $__pypt_set_install') != 0:
                    log.err("FATAL: Something is wrong with the apt system.\n")
            else:
                parser.error("This argument is supported only on Unix like systems with apt installed\n")
                sys.exit(0)
               
        if options.fetch_update and options.fetch_upgrade:
            if os.access(options.fetch_update, os.F_OK) and os.access(options.fetch_upgrade, os.F_OK):
                log.msg("\nFetching uris which update apt's package database\n\n")
            	# Since we're in fetch_update, the download_type will be non-deb/rpm data
            	# 1 is for update packages 
            	# 2 is for upgrade packages
            	fetcher(options, 1)
                sys.exit(0)
            else:
                log.err("\nFile not present. Check path.\n")
                sys.exit(1)
                
        if options.fetch_update:
            if os.access(options.fetch_update, os.F_OK):
                log.msg("\nFetching packages which need upgradation\n\n")
            	# Since we're in fetch_update, the download_type will be non-deb/rpm data
            	# 1 is for update packages 
            	# 2 is for upgrade packages
            	fetcher(options, 2)
            	sys.exit(0)
            else:
                log.err("\n%s file not present. Check path.\n" % (options.fetch_upgrade) )
                sys.exit(1)
                 
        if options.fetch_upgrade:
            if os.access(options.fetch_upgrade, os.F_OK):
                log.msg("\nFetching packages which need upgradation\n\n")
            	# Since we're in fetch_update, the download_type will be non-deb/rpm data
            	# 1 is for update packages 
            	# 2 is for upgrade packages
            	fetcher(options, 2)
            	sys.exit(0)
            else:
                log.err("\n%s file not present. Check path.\n" % (options.fetch_upgrade) )
                sys.exit(1)
                 
        if options.install_update:
            #INFO: Comment these lines to do testing on Windows machines too
            if os.geteuid() != 0:
                log.err("\nYou need superuser privileges to execute this option\n")
                sys.exit(1)
                
            if os.path.isfile(options.install_update) is True:
                # Okay! We're a file. It should be a zip file
                syncer(options, 1)
            elif os.path.isdir(options.install_update) is True:
                # We're a directory
                syncer(options, 2)
            else:
                log.err("Aieee! %s is unsupported format\n" % (options.install_update))
            sys.exit(0)
            
        if options.install_upgrade:
            #INFO: Comment these lines to do testing on Windows machines too
            if os.geteuid() != 0:
                log.err("\nYou need superuser privileges to execute this option\n")
                sys.exit(1)
            if os.path.isfile(options.install_upgrade) is True:
                syncer(options, 1)
            elif os.path.isdir(options.install_upgrade) is True:
                syncer(options, 2)
            else:
                log.err("Aieee! %s is unsupported format\n" % (options.install_upgrade))
            sys.exit(0)
            
    except KeyboardInterrupt:
        log.err("\nInterrupted by user. Exiting!\n")
        sys.exit(1)        