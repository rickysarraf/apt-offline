
############################################################################
#    Copyright (C) 2005, 2009 Ritesh Raj Sarraf                            #
#    rrs@researchut.com                                                    #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 3 of the License, or     #
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
import shutil
import platform
import string
import urllib2
import Queue
import threading
import socket
import tempfile

import zipfile

# Given the merits of argparse, I hope it'll soon be part
# of the Python Standard Library.
# http://code.google.com/argparse
# Till then we use it this way.
try:
        import argparse
except ImportError:
        import AptOffline_argparse as argparse

# On Debian, python-debianbts package provides this library
DebianBTS = True
try:
        import AptOfflineDebianBtsLib
except ImportError:
        DebianBTS = False

import AptOfflineMagicLib

guiBool = True
try:
        from qt import *
        from AptOfflineGUI import pyptofflineguiForm
except ImportError:
        guiBool = False
    
#INFO: Check if python-apt is installed
PythonApt = True
try:
        import apt
        import apt_pkg
except ImportError:
        PythonApt = False
PythonApt = False #Remove it after porting to python-apt
    
import AptOfflineLib

#INFO: Set the default timeout to 30 seconds for the packages that are being downloaded.
socket.setdefaulttimeout(30)

# How many times should we retry on socket timeouts
SOCKET_TIMEOUT_RETRY = 5

'''This is the core module. It does the main job of downloading packages/update packages,\n
figuring out if the packages are in the local cache, handling exceptions and many more stuff'''


app_name = "apt-offline"
version = "0.9.6"
copyright = "(C) 2005 - 2010 Ritesh Raj Sarraf"
terminal_license = "This program comes with ABSOLUTELY NO WARRANTY.\n\
This is free software, and you are welcome to redistribute it under\n\
the GNU GPL Version 3 (or later) License\n"
        
errlist = []
supported_platforms = ["Linux", "GNU/kFreeBSD", "GNU"]
apt_update_target_path = '/var/lib/apt/lists/partial'
apt_update_final_path = '/var/lib/apt/lists/'
apt_package_target_path = '/var/cache/apt/archives/'

apt_bug_file_format = "__apt__bug__report"
IgnoredBugTypes = ["Resolved bugs", "Normal bugs", "Minor bugs", "Wishlist items", "FIXED"]


#These are spaces which will overwrite the progressbar left mess
LINE_OVERWRITE_SMALL = " " * 10
LINE_OVERWRITE_MID = " " * 30
LINE_OVERWRITE_FULL = " " * 60

       
class FetchBugReports( AptOfflineLib.Archiver ):
        def __init__( self, apt_bug_file_format, IgnoredBugTypes, ArchiveFile=None, lock=False ):
                self.bugsList = []
                self.IgnoredBugTypes = IgnoredBugTypes
                self.lock = lock
                self.apt_bug = apt_bug_file_format
        
                if self.lock:
                        AptOfflineLib.Archiver.__init__( self, lock )
                        self.ArchiveFile = ArchiveFile
        
        def FetchBugsDebian( self, PackageName, Filename=None ):
                '''0 => False
                1 => No Bug Reports
                2 => True'''
                
                if Filename != None:
                        try:
                                file_handle = open( Filename, 'a' )
                        except IOError:
                                sys.exit( 1 )
                
                try:
                        ( num_of_bugs, header, self.bugs_list ) = AptOfflineDebianBtsLib.get_reports( PackageName )
                except socket.timeout:
                        return 0
                
                if num_of_bugs:
                        atleast_one_bug_report_downloaded = False
                        for x in self.bugs_list:
                                ( sub_bugs_header, sub_bugs_list ) = x
                                
                                #INFO: We filter all the IgnoredBugTypes that we think aren't necessary.
                                #We don't download those low priority bug reports
                                for BugType in self.IgnoredBugTypes:
                                        if BugType in sub_bugs_header:
                                                bug_flag = 0
                                                break
                                        bug_flag = 1
                                
                                if bug_flag:
                                        for x in sub_bugs_list:
                                                break_bugs = x.split( ' ' )
                                                bug_num = string.lstrip( break_bugs[0], '#' )
                                                try:
                                                        data = AptOfflineDebianBtsLib.get_report( bug_num, followups=True )
                                                except socket.timeout:
                                                        return False
                                                if Filename == None:
                                                        self.fileName = PackageName + "." + bug_num + "." + self.apt_bug
                                                        file_handle = open( self.fileName, 'w' )
                                                else:
                                                        self.fileName = Filename
                                                        file_handle = open( self.fileName, 'a' )
                            
                                                file_handle.write( data[0] + "\n\n" )
                                                for x in data[1]:
                                                        file_handle.write( x )
                                                        file_handle.write( "\n" )
                                                file_handle.write( "\n" * 3 )
                                                file_handle.flush()
                                                file_handle.close()
                                                #We're adding to an archive file here.
                                                if self.lock:
                                                        self.AddToArchive( self.ArchiveFile, self.fileName )
                                                atleast_one_bug_report_downloaded = True
                        if atleast_one_bug_report_downloaded:
                                return 2
                        else:
                                return 1
                else:
                        #FIXME: When no bug reports are there, i.e. bug count is 0, we hit here
                        # We shouldn't be returning False
                        return 1
                
        def AddToArchive(self, ArchiveFile, fileName):
                if self.compress_the_file(ArchiveFile, fileName):
                        os.unlink(fileName)
                return True
        
        
def files(root): 
        for path, folders, files in os.walk(root): 
                for file in files: 
                        yield path, file 
    
    
def find_first_match(cache_dir=None, filename=None):
        '''Return the full path of the filename if a match is found
        Else Return False'''
        
        # Do the sanity check first
        #if cache_dir is None or filename is None or os.path.isdir(cache_dir) is False:
        if cache_dir is None:
                return False
        elif filename is None:
                return False
        elif os.path.isdir(cache_dir) is False:
                return False
        else:
                for path, file in files(cache_dir): 
                        if file == filename:
                                return os.path.join(path, file)
                return False
        
        
class DownloadFromWeb(AptOfflineLib.ProgressBar):
        '''Class for DownloadFromWeb
        This class also inherits progressbar functionalities from
        parent class, ProgressBar'''
        
        def __init__(self, width, total_items):
                '''width = Progress Bar width'''
                AptOfflineLib.ProgressBar.__init__(self, width=width, total_items=total_items)
        
        def download_from_web(self, url, file, download_dir):
                '''url = url to fetch
                file = file to save to
                donwload_dir = download path'''
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
     
                        socket_counter = 0
                        while i < size:
                                socket_timeout = None
                                try:
                                        data.write (temp.read(block_size))
                                except socket.timeout, timeout:
                                        socket_timeout = True
                                        socket_counter += 1
                                except socket.error, error:
                                        socket_timeout = True
                                        socket_counter += 1
                                if socket_counter == SOCKET_TIMEOUT_RETRY:
                                        errfunc(101010, "Max timeout retry count reached. Discontinuing download.\n", url)
                                        
                                        # Clean the half downloaded file.
                                        os.unlink(file)
                                        return False
                                
                                if socket_timeout is True:
                                        errfunc(10054, "Socket Timeout. Retry - %d\n" % (socket_counter) , url)
                                        continue
                
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
                        errfunc(errno, strerror, download_dir)
                except urllib2.HTTPError, errstring:
                        errfunc(errstring.code, errstring.msg, url)
                except urllib2.URLError, errstring:
                        #INFO: Weird. But in urllib2.URLError, I noticed that for
                        # error type "timeouts", no errno was defined.
                        # errstring.errno was listed as None 
                        # In my tests, wget categorized this behavior as:
                        # 504: gateway timeout
                        # So I am doing the same here.
                        if errstring.errno is None:
                                errfunc(504, errstring.reason, url)
                        else:
                                errfunc(errstring.errno, errstring.reason, url)
                except IOError, e:
                        if hasattr(e, 'reason'):
                                log.err("%s\n" % (e.reason))
                        if hasattr(e, 'code') and hasattr(e, 'reason'):
                                errfunc(e.code, e.reason, file)
                except socket.timeout:
                        errfunc(10054, "Socket timeout.\n", url)


def stripper(item):
        '''Strips extra characters from "item".
        Breaks "item" into:
        url - The URL
        file - The actual package file
        size - The file size
        checksum - The checksum string
        and returns them.'''
    
        item = item.split(' ')
        url = string.rstrip(string.lstrip(''.join(item[0]), chars="'"), chars="'")
        file = string.rstrip(string.lstrip(''.join(item[1]), chars="'"), chars="'")
        size = int(string.rstrip(string.lstrip(''.join(item[2]), chars = "'"), chars="'"))
        #INFO: md5 ends up having '\n' with it.
        # That needs to be stripped too.
        checksum = string.rstrip(string.lstrip(''.join(item[3]), chars = "'"), chars = "'")
        checksum = string.rstrip(checksum, chars = "\n")
    
        return url, file, size, checksum


def errfunc(errno, errormsg, filename):
        '''We use errfunc to handler errors.
        There are some error codes (-3 and 13 as of now)
        which are temporary codes, they happen when there
        is a temporary resolution failure, for example.
        For such situations, we can't abort because the
        uri file might have other hosts also, which might
        be well accessible.
        This function does the job of behaving accordingly
        as per the error codes.'''
        error_codes = [-3, 13, 504, 404, 401, 10060, 104, 101010]
        # 104, 'Connection reset by peer'
        # 504 is for gateway timeout
        # 404 is for URL error. Page not found.
        # 401 is for Restricted pages
        # 10060 is for Operation Time out. There can be multiple reasons for this timeout
        # 101010 is for socket max retry count
        # 10054 is for Socket Timeout. Socket Timeout are seen during network congestion
    
        #TODO: Find out what these error codes are for
        # and better document them the next time you find it out.
        # 13 is for "Permission Denied" when you don't have privileges to access the destination 
        if errno in error_codes:
                log.err("%s - %s - %s.%s\n" % (filename, errno, errormsg, LINE_OVERWRITE_MID))
                log.verbose("Will still try with other package uris\n")
                pass
        elif errno == 10054:
                log.verbose("%s - %s - %s.%s\n" % (filename, errno, errormsg, LINE_OVERWRITE_SMALL) )
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
                log.err("I don't understand this error code %s\nPlease file a bug report" % (errno))
        
        
def get_pager_cmd(pager_cmd = None):
        if os.name == 'posix':
                default_pager_cmd = 'less -r'
        elif os.name in ['nt', 'dos']:
                default_pager_cmd = 'type'
        
        if pager_cmd is None:
                try:
                        pager_cmd = os.environ['PAGER']
                except:
                        pager_cmd = default_pager_cmd
                return pager_cmd


class PagerCmd:
        '''Tries to automatically detect and set the pager on the running OS'''
        def __init__(self, pager_cmd = None):
                if os.name == 'posix':
                        self.default_pager_cmd = 'less -r'
                elif os.name in ['nt', 'dos']:
                        self.default_pager_cmd = 'type'
                
                if pager_cmd is None:
                        try:
                                self.pager_cmd = os.environ['PAGER']
                        except:
                                self.pager_cmd = self.default_pager_cmd
        
        def send_to_pager(self, String = None):
                '''Writes the String to the pager'''
                if String is None:
                        return False
                else:
                        try:
                                retval = None # None is correct. On success, None is returned
                                pager = os.popen(self.pager_cmd, 'w')
                                pager.write(String)
                                retval = pager.close()
                        except IOError,msg:  # broken pipe when user quits
                                if msg.args == (32,'Broken pipe'):
                                        retval = None
                                else:
                                        retval = 1
                        except OSError:
                                retval = 1
                        return retval
            

def fetcher( args ):
        
        # get opts
        Str_GetArg = args.get
        Int_SocketTimeout = args.socket_timeout
        Str_DownloadDir = args.download_dir
        Str_CacheDir = args.cache_dir
        Bool_DisableMD5Check = args.disable_md5check
        Int_NumOfThreads = args.num_of_threads
        Str_BundleFile = args.bundle_file
        #Bool_GetUpdate = args.get_update
        #Bool_GetUpgrade = args.get_upgrade
        Bool_BugReports = args.deb_bugs
        
        if Int_SocketTimeout:
                try:
                        Int_SocketTimeout.__int__()
                        socket.setdefaulttimeout( Int_SocketTimeout )
                        log.verbose( "Default timeout now is: %d.\n" % ( socket.getdefaulttimeout() ) )
                except AttributeError:
                        log.err( "Incorrect value set for socket timeout.\n" )
                        sys.exit( 1 )
        
        #INFO: Python 2.5 has hashlib which supports sha256
        # If we don't have Python 2.5, disable MD5/SHA256 checksum
        if AptOfflineLib.Python_2_5 is False:
                Bool_DisableMD5Check = True
                log.verbose( "\nMD5/SHA256 Checksum is being disabled. You need atleast Python 2.5 to do checksum verification.\n" )
        
        if Str_GetArg:
                if os.path.isfile(Str_GetArg):
                        log.msg( "\nFetching APT Data\n\n" )
                else:
                        log.err( "File not present. Check path.\n" )
                        sys.exit( 1 )
                        
        if Str_CacheDir is not None:
                if os.path.isdir( Str_CacheDir ) is False:
                        log.verbose( "WARNING: cache dir %s is incorrect. Did you give the full path ?\n" % (Str_CacheDir) )
        
        class FetcherClass( DownloadFromWeb, AptOfflineLib.Archiver, AptOfflineLib.Checksum ):
                def __init__( self, width, lock, total_items ):
                        DownloadFromWeb.__init__( self, width=width, total_items=total_items )
                        #ProgressBar.__init__(self, width)
                        #self.width = width
                        AptOfflineLib.Archiver.__init__( self, lock=lock )
                        #self.lock = lock
        
        if Str_DownloadDir is None:
                tempdir = tempfile.gettempdir()
                if os.access( tempdir, os.W_OK ) is True:
                        pidname = os.getpid()
                        tempdir = os.path.join(tempdir , "apt-offline-downloads-" + str(pidname) )
                        os.mkdir(tempdir)
                                
                        Str_DownloadDir = os.path.abspath(tempdir)
                else:
                        log.err( "%s is not writable\n" % (tempdir) ) 
                        errfunc ( 1, '')
        else:
                if os.access( Str_DownloadDir, os.W_OK ) is True:
                        Str_DownloadDir = os.path.abspath( Str_DownloadDir )
                else:
                        #INFO: If the path is provided, but doesn't exist
                        # Create it.
                        try:
                                os.umask( 0002 )
                                os.mkdir( Str_DownloadDir )
                                Str_DownloadDir = os.path.abspath( Str_DownloadDir )
                        except:
                                log.err( "I couldn't create directory %s\n" % (Str_DownloadDir) )
                                errfunc( 1, '' )
                                
        if Str_BundleFile is not None:
                Str_BundleFile = os.path.abspath(Str_BundleFile)
                if os.access(Str_BundleFile, os.F_OK ):
                        log.err( "%s already present.\nRemove it first.\n" % ( Str_BundleFile ) )
                        sys.exit( 1 )
        
        if Bool_BugReports:
                if DebianBTS is True:
                        if Str_BundleFile is not None:
                                #INFO: We are creating an archive then.
                                # For now, we support zip archives
                                FetchBugReportsDebian = FetchBugReports( apt_bug_file_format, IgnoredBugTypes, Str_BundleFile, lock=True )
                        else:
                                #INFO: No bundle file to be created.
                                # Data will be stored in the Str_DownloadDir folder
                                FetchBugReportsDebian = FetchBugReports( apt_bug_file_format, IgnoredBugTypes )
                else:
                        log.err( "Couldn't find debianbts module.\n Cannot fetch Bug Reports.\n" )
        
        FetchData = {} #Info: Initialize an empty dictionary.
        
        #INFO: We don't distinguish in between what to fetch
        # We just rely on what a signature file lists us to get
        # It can be just debs or just package updates or both
        if Str_GetArg is not None:
                try:
                        raw_data_list = open( Str_GetArg, 'r' ).readlines()
                except IOError, ( errno, strerror ):
                        log.err( "%s %s\n" % ( errno, strerror ) )
                        errfunc( errno, '' )
                        
                FetchData['Item'] = []
                for item in raw_data_list:
                        FetchData['Item'].append( item )
        del raw_data_list
        
        # INFO: Let's get the total number of items. This will get the
        # correct total count in the progress bar.
        total_items = len(FetchData['Item'])
        
        #global FetcherInstance
        FetcherInstance = FetcherClass( width=30, lock=True, total_items=total_items )
        
        #INFO: Thread Support
        if Int_NumOfThreads > 2:
                log.msg("WARNING: If you are on a slow connection, it is good to\n")
                log.msg("WARNING: limit the number of threads to a low number like 2.\n")
                log.msg("WARNING: Else higher number of threads executed could cause\n")
                log.msg("WARNING: network congestion and timeouts.\n\n")
        
        def abc(request, response, func=find_first_match):
                '''Get items from the request Queue, process them
                with func(), put the results along with the
                Thread's name into the response Queue.
                Stop running when item is None.'''
                #while 1:
                #tuple_item_key = request.get()
                #if tuple_item_key is None:
                #        break
                #(key, item) = tuple_item_key
                
                (key, item) = request
                
                #INFO: Everything
                (url, file, download_size, checksum) = stripper(item)
                thread_name = threading.currentThread().getName()
                log.verbose("Thread is %s\n" % (thread_name) )
                
                if url.endswith(".deb"):
                        try:
                                PackageName = file.split("_")[0]
                        except IndexError:
                                log.err("Not getting a package name here is problematic. Better bail out.\n")
                                sys.exit(1)
                        
                        #INFO: For Package version, we don't want to fail
                        try:
                                PackageVersion = file.split("_")[1]
                        except IndexError:
                                PackageVersion = "NA"
                                log.verbose("Weird!! Package version not present. Is it really a deb file?\n")
                        
                        
                        #INFO: find_first_match() returns False or a file name with absolute path
                        full_file_path = func(Str_CacheDir, file)
                        #INFO: If we find the file in the local Str_CacheDir, we'll execute this block.
                        if full_file_path != False:
                                # We'll first check for its md5 checksum
                                if Bool_DisableMD5Check is False:
                                        if FetcherInstance.CheckHashDigest(full_file_path, checksum) is True:
                                                log.verbose("Checksum correct for package %s.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                
                                                bug_fetched = False
                                                if Bool_BugReports:
                                                        log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                        if FetchBugReportsDebian.FetchBugsDebian(PackageName) in [1,2]:
                                                                log.verbose("Fetched bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                                bug_fetched = True
                                                        else:
                                                                log.verbose("Couldn't fetch bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                                
                                                if Str_BundleFile:
                                                        if FetcherInstance.compress_the_file(Str_BundleFile, full_file_path) is True:
                                                                log.success("%s copied from local cache directory %s.%s\n" % (PackageName, Str_CacheDir, LINE_OVERWRITE_MID) )
                                                        else:
                                                                log.err("Couldn't add %s to archive %s.%s\n" % (file, Str_BundleFile, LINE_OVERWRITE_MID) )
                                                                sys.exit(1)
                                                #INFO: If no zip option enabled, simply copy the downloaded package file
                                                # along with the downloaded bug reports.
                                                else:
                                                        try:
                                                                shutil.copy(full_file_path, Str_DownloadDir)
                                                                log.success("%s copied from local cache directory %s.%s\n" % (PackageName, Str_CacheDir, LINE_OVERWRITE_MID) )
                                                        except shutil.Error:
                                                                log.verbose("%s already available in %s. Skipping copy!!!%s\n" % (file, Str_DownloadDir, LINE_OVERWRITE_MID) )
                                                        
                                                        if bug_fetched is True:
                                                                for x in os.listdir(os.curdir):
                                                                        if (x.startswith(PackageName) and x.endswith(apt_bug_file_format) ):
                                                                                shutil.move(x, Str_DownloadDir)
                                                                                log.verbose("Moved %s file to %s folder.%s\n" % (x, Str_DownloadDir, LINE_OVERWRITE_FULL) )
                                        #INFO: Damn!! The md5chesum didn't match :-(
                                        # The file is corrupted and we need to download a new copy from the internet
                                        else:
                                                log.verbose("%s checksum mismatch. Skipping file.%s\n" % (file, LINE_OVERWRITE_FULL) )
                                                log.msg("Downloading %s - %s %s\n" % (PackageName, log.calcSize(download_size/1024), LINE_OVERWRITE_MID) )
                                                if FetcherInstance.download_from_web(url, file, Str_DownloadDir) == True:
                                                        log.success("\r%s done.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                        
                                                        #Add to Str_CacheDir if possible
                                                        if Str_CacheDir and os.access(Str_CacheDir, os.W_OK) == True:
                                                                try:
                                                                        shutil.copy(file, Str_CacheDir)
                                                                        log.verbose("%s copied to local cache directory %s.%s\n" % (file, Str_CacheDir, LINE_OVERWRITE_MID) )
                                                                except shutil.Error:
                                                                        log.verbose("Couldn't copy %s to %s.%s\n" % (file, Str_CacheDir, LINE_OVERWRITE_FULL) )
                                                        else:
                                                                log.verbose("cache_dir %s is not writeable. Skipping copy to it.\n" % (Str_CacheDir) )
                                                        
                                                        #Fetch bug reports
                                                        if Bool_BugReports:
                                                                log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                                if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                                        log.verbose( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                                else:
                                                                        log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                        if Str_BundleFile:
                                                                if FetcherInstance.compress_the_file( Str_BundleFile, file ) != True:
                                                                        log.err( "Couldn't archive %s to file %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        sys.exit( 1 )
                                                                else:
                                                                        log.verbose( "%s added to archive %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        os.unlink( os.path.join( Str_DownloadDir, file ) )
                                #INFO: You're and idiot.
                                # You should NOT disable md5checksum for any files
                                else:
                                        bug_fetched = False
                                        if Bool_BugReports:
                                                log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                        log.verbose( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                        bug_fetched = True
                                                else:
                                                        log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                            
                                        #FIXME: Don't know why this was really required. If this has no changes, delete it.
                                        #file = full_file_path.split("/")
                                        #file = file[len(file) - 1]
                                        #file = download_path + "/" + file
                                        if Str_BundleFile:
                                                if FetcherInstance.compress_the_file( Str_BundleFile, file ) != True:
                                                        log.err( "Couldn't archive %s to file %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                        sys.exit( 1 )
                                                else:
                                                        log.verbose( "%s added to archive %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                        os.unlink( os.path.join( Str_DownloadDir, file ) )
                                        else:
                                                # Since zip file option is not enabled let's copy the file to the target folder
                                                try:
                                                        shutil.copy( full_file_path, Str_DownloadDir )
                                                        log.success( "%s copied from local cache directory %s.%s\n" % ( file, Str_CacheDir, LINE_OVERWRITE_SMALL ) )
                                                except shutil.Error:
                                                        log.verbose( "%s already available in dest_dir. Skipping copy!!!%s\n" % ( file, LINE_OVERWRITE_SMALL ) )
                            
                                                # And also the bug reports
                                                if bug_fetched is True:
                                                        for x in os.listdir( os.curdir ):
                                                                if ( x.startswith( PackageName ) and x.endswith( apt_bug_file_format ) ):
                                                                        shutil.move( x, Str_DownloadDir )
                                                                        log.verbose( "Moved %s file to %s folder.%s\n" % ( x, Str_DownloadDir, LINE_OVERWRITE_MID ) )
                                
                        else:
                                #INFO: This block gets executed if the file is not found in local Str_CacheDir or Str_CacheDir is None
                                # We go ahead and try to download it from the internet
                                log.verbose( "%s not available in local cache %s.%s\n" % ( file, Str_CacheDir, LINE_OVERWRITE_MID ) )
                                log.msg( "Downloading %s %s - %s %s\n" % ( PackageName, PackageVersion, log.calcSize( download_size / 1024 ), LINE_OVERWRITE_MID ) )
                                if FetcherInstance.download_from_web( url, file, Str_DownloadDir ) == True:
                                        #INFO: This block gets executed if md5checksum is allowed
                                        if Bool_DisableMD5Check is False:
                                                #INFO: Debian moved to SHA256. So we use that now. Older systems could have md5
                                                log.verbose( "File %s has checksum %s\n" % ( file, checksum ) )
                                                if FetcherInstance.CheckHashDigest( file, checksum ) is True:
                                                        if Str_CacheDir and os.access( Str_CacheDir, os.W_OK ) == True:
                                                                try:
                                                                        shutil.copy( file, Str_CacheDir )
                                                                        log.verbose( "%s copied to local cache directory %s.%s\n" % ( file, Str_CacheDir, LINE_OVERWRITE_MID ) )
                                                                except shutil.Error:
                                                                        log.verbose( "%s already available in %s. Skipping copy!!!%s\n" % ( file, Str_CacheDir, LINE_OVERWRITE_MID ) )
                                                        else:
                                                                log.verbose( "Str_CacheDir %s is not writeable. Skipping copy to it.\n" % ( Str_CacheDir ) )
                                    
                                                        if Bool_BugReports:
                                                                log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                                if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                                        log.verbose( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                                else:
                                                                        log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                    
                                                        if Str_BundleFile:
                                                                if FetcherInstance.compress_the_file( Str_BundleFile, file ) != True:
                                                                        log.err( "Couldn't archive %s to file %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        sys.exit( 1 )
                                                                else:
                                                                        log.verbose( "%s added to archive %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        os.unlink( os.path.join( Str_DownloadDir, file ) )
                                                        log.success( "\r%s %s done.%s\n" % ( PackageName, PackageVersion, LINE_OVERWRITE_FULL ) )
                                                else:
                                                        #INFO MD5 Checksum is incorrect.
                                                        log.err( "%s Checksum mismatch.\n" % ( PackageName ) )
                                                        errlist.append( PackageName )
                                        else:
                                                if Bool_BugReports:
                                                        log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                        if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                                log.verbose( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                        else:
                                                                log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                
                                                if Str_BundleFile:
                                                        if FetcherInstance.compress_the_file( Str_BundleFile, file ) != True:
                                                                log.err( "Couldn't archive %s to file %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                sys.exit( 1 )
                                                        else:
                                                                log.verbose( "%s added to archive %s.%s\n" % ( file, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                os.unlink( os.path.join( Str_DownloadDir, file ) )
                                    
                                                log.success( "\r%s %s done.%s\n" % ( PackageName, PackageVersion, LINE_OVERWRITE_FULL ) )
                                else:
                                        errlist.append( PackageName )
                                        
                else:
                        #INFO: We are a package update
                        PackageName = url
                        log.msg("Downloading %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) ) 
                        if FetcherInstance.download_from_web(url, file, Str_DownloadDir) == True:
                                log.success("\r%s done.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                if Str_BundleFile:
                                        if FetcherInstance.compress_the_file(Str_BundleFile, file) != True:
                                                log.err("Couldn't archive %s to file %s.%s\n" % (file, Str_BundleFile, LINE_OVERWRITE_MID) )
                                                sys.exit(1)
                                        else:
                                                log.verbose("%s added to archive %s.%s\n" % (file, Str_BundleFile, LINE_OVERWRITE_FULL) )
                                                os.unlink(os.path.join(Str_DownloadDir, file) )
                        else:
                                errlist.append(url)
                        
        # Create two Queues for the requests and responses
        requestQueue = Queue.Queue()
        responseQueue = Queue.Queue()
        
        
        ConnectThread = AptOfflineLib.MyThread(abc, requestQueue, responseQueue, Int_NumOfThreads)
        
        ConnectThread.startThreads()
        
        # Queue up the requests.
        #for item in raw_data_list: requestQueue.put(item)
        for key in FetchData.keys():
                for item in FetchData.get(key):
                        ConnectThread.populateQueue( (key, item) )
        ConnectThread.stopThreads()
        ConnectThread.stopQueue()
        
                
        # Print the failed files
        if len(errlist) > 0:
                log.msg("\n\n")
                log.err("The following files failed to be downloaded.\n")
                for error in errlist:
                        log.err("%s failed.\n" % (error))
        if args.bundle_file:
                log.msg("\nDownloaded data to %s\n" % (Str_BundleFile) )
        else:
                log.msg("\nDownloaded data to %s\n" % (Str_DownloadDir) )
        
def installer( args ):
        
        class APTVerifySigs:
                
                def __init__(self, gpgv=None, keyring=None):
                        if gpgv is None:
                                self.gpgv="/usr/bin/gpgv"
                        else:
                                self.gpgv=gpgv
                                
                        if keyring is None:
                                self.opts="--keyring /etc/apt/trusted.gpg --ignore-time-conflict"
                        else:
                                self.opts = "--keyring %s --ignore-time-conflict" % (keyring)
                                
                def VerifySig(self, signature_file, signed_file):
                        
                        if not os.access(signature_file, os.F_OK):
                                log.err("%s is bad. Can't proceed.\n" % (signature_file) )
                                return False
                        if not os.access(signed_file, os.F_OK):
                                log.err("%s is bad. Can't proceed.\n" % (signed_file) )
                                return False
                        
                        x = os.system("%s %s %s %s" % (self.gpgv, self.opts, signature_file, signed_file) )
                        #TODO: Find a way to redirect std[out|err]
                        # look at subprocess module
                        
                        if x == 0:
                                return True
                        else:
                                return False
                
        
        # install opts
        Str_InstallArg = args.install
        Bool_TestWindows = args.simulate
        Bool_SkipBugReports = args.skip_bug_reports
        Bool_Untrusted = args.allow_unauthenticated
        Str_InstallSrcPath = args.install_src_path
        
        
        # Old cruft. Needs clean-up
        install_file_path = Str_InstallArg
        
        if Str_InstallSrcPath is None:
                tempdir = tempfile.gettempdir()
                if os.access( tempdir, os.W_OK ) is True:
                        pidname = os.getpid()
                        tempdir = os.path.join(tempdir , "apt-offline-src-downloads-" + str(pidname) )
                        os.mkdir(tempdir)
                                
                        Str_InstallSrcPath = os.path.abspath(tempdir)
                else:
                        log.err( "%s is not writable\n" % (tempdir) ) 
                        sys.exit(1)
        if not os.path.isdir(Str_InstallSrcPath):
                log.err("Not a folder.\n")
                sys.exit(1)
        if os.access(Str_InstallSrcPath, os.W_OK) is not True:
                log.err("%s is not writable.\n" % (Str_InstallSrcPath))
                sys.exit(1)
                
        if Str_InstallArg:
                if Bool_TestWindows:
                        global apt_package_target_path
                        tempdir = tempfile.gettempdir()
                        if os.access( tempdir, os.W_OK ) is True:
                                pidname = os.getpid()
                                tempdir = os.path.join(tempdir , "apt-package-target-path-" + str(pidname) )
                                log.verbose("apt-package-target-path is %s\n" % (tempdir) )
                                os.mkdir(tempdir)
                                        
                                apt_package_target_path = os.path.abspath(tempdir)
                        else:
                                log.err( "%s is not writable\n" % (tempdir) ) 
                                sys.exit(1)
                                
                        global apt_update_target_path
                        tempdir = tempfile.gettempdir()
                        if os.access( tempdir, os.W_OK ) is True:
                                pidname = os.getpid()
                                tempdir = os.path.join(tempdir , "apt-update-target-path-" + str(pidname) )
                                log.verbose("apt-update-target-path is %s\n" % (tempdir) )
                                os.mkdir(tempdir)
                                        
                                apt_update_target_path = os.path.abspath(tempdir)
                        else:
                                log.err( "%s is not writable\n" % (tempdir) ) 
                                sys.exit(1)
                                
                        global apt_update_final_path
                        tempdir = tempfile.gettempdir()
                        if os.access( tempdir, os.W_OK ) is True:
                                pidname = os.getpid()
                                tempdir = os.path.join(tempdir , "apt-update-final-path-" + str(pidname) )
                                log.verbose("apt-update-final-path is %s\n" % (tempdir) )
                                os.mkdir(tempdir)
                                        
                                apt_update_final_path = os.path.abspath(tempdir)
                        else:
                                log.err( "%s is not writable\n" % (tempdir) ) 
                                sys.exit(1)
                else:
                        try:
                                if os.geteuid() != 0:
                                        log.err("You need superuser privileges to execute this option\n")
                                        sys.exit(1)
                        except AttributeError:
                                log.err("Are you really running the install command on a Debian box?\n")
                                sys.exit(1)
                                
        archive = AptOfflineLib.Archiver()
        archive_file_types = ['application/x-bzip2', 'application/gzip', 'application/zip']
        
        if not Bool_Untrusted:
                AptSecure = APTVerifySigs()
                
        try:
                #INFO: Let's clean the partial database
                for x in os.listdir(apt_update_target_path):
                        x = os.path.join(apt_update_target_path, x)
                        if os.access(x, os.W_OK):
                                os.unlink(x)
                                log.verbose("Cleaning old update data file %s.\n" % (x) )
        except OSError:
                log.err("Cannot find APT's partial cache dir %s\n" % (apt_update_target_path) )
                sys.exit(1)
                
        
        def display_options():
                log.msg( "(Y) Yes. Proceed with installation\n" )
                log.msg( "(N) No, Abort.\n" )
                log.msg( "(R) Redisplay the list of bugs.\n" )
                log.msg( "(Bug Number) Display the bug report from the Offline Bug Reports.\n" )
                log.msg( "(?) Display this help message.\n" )
        
        def get_response():
                response = raw_input( "What would you like to do next:\t (y, N, Bug Number, R, ?)" )
                response = response.rstrip( "\r" )
                return response
    
        def list_bugs(dictList):
                '''
                Takes a dictionary of key,value pair where:
                key => filename
                value => subject string
                '''
                log.msg( "\n\nFollowing are the list of bugs present.\n" )
                for each_bug in dictList.keys():
                        bug_num = each_bug.split( '.' )[-2]
                        bug_subject = dictList[each_bug]
                        log.msg( "%s\t%s\n" % ( bug_num, bug_subject ) )
            
        def magic_check_and_uncompress( archive_file=None, filename=None):
                retval = False
                if AptOfflineMagicLib.file( archive_file ) == "application/x-bzip2" or \
                AptOfflineMagicLib.file( archive_file ) == "application/x-gzip":
                        temp_filename = os.path.join(apt_update_target_path, filename + app_name)
                        filename = os.path.join(apt_update_target_path, filename)
                        if AptOfflineMagicLib.file( archive_file ) == "application/x-bzip2":
                                retval = archive.decompress_the_file( archive_file, temp_filename, "bzip2" )
                        elif AptOfflineMagicLib.file( archive_file ) == "application/x-gzip":
                                retval = archive.decompress_the_file( archive_file, temp_filename, "gzip" )
                        else:
                                retval = False
                        if retval is True:
                                os.rename(temp_filename, filename)
                        else:
                                os.unlink(temp_filename)
                elif AptOfflineMagicLib.file( archive_file ) == "application/zip":
                        retval = archive.decompress_the_file( os.path.join( install_file_path, eachfile ), apt_update_target_path, eachfile, "zip" )
                elif AptOfflineMagicLib.file( archive_file ) == "PGP armored data":
                        filename = os.path.join(apt_update_target_path, filename)
                        shutil.copy2(archive_file, filename)
                        # PGP armored data should be bypassed
                        log.verbose("File is %s, hence 'True'.\n" % (filename) )
                        retval = True
                elif AptOfflineMagicLib.file( archive_file ) == "application/x-dpkg":
                        filename = os.path.join(apt_package_target_path, filename)
                        if os.access( apt_package_target_path, os.W_OK ):
                                shutil.copy2( archive_file, filename )
                                log.msg("%s file synced.\n" % (filename) )
                                retval = True
                        else:
                                log.err( "Cannot write to target path %s\n" % ( apt_package_target_path ) )
                                sys.exit( 1 )
                elif filename.endswith( apt_bug_file_format ):
                        pass
                elif AptOfflineMagicLib.file( archive_file ) == "ASCII text":
                        filename = os.path.join(apt_update_target_path, filename)
                        if os.access( apt_update_target_path, os.W_OK ):
                                shutil.copy( archive_file, filename )
                                retval = True
                        else:
                                log.err( "Cannot write to target path %s\n" % ( apt_update_target_path ) )
                                sys.exit( 1 )
                else:
                        log.err( "I couldn't understand file type %s.\n" % ( filename ) )
                
                if retval:
                        log.verbose( "%s file synced to %s.\n" % ( filename, apt_update_target_path ) )
        
        if os.path.isfile(install_file_path):
                #INFO: For now, we support zip bundles only
                file = zipfile.ZipFile( install_file_path, "r" )
                
                SrcPkgDict = {}
                for filename in file.namelist():
                        if filename.endswith(".dsc"):
                                SrcPkgName = filename.split('_')[0]
                                temp = tempfile.NamedTemporaryFile()
                                temp.file.write( file.read( filename ) )
                                temp.file.flush()
                                temp.file.seek( 0 ) #Let's go back to the start of the file
                                SrcPkgDict[SrcPkgName] = []
                                for SrcPkgIdentifier in temp.file.readlines():
                                        if SrcPkgIdentifier.startswith(' ') and not SrcPkgIdentifier.isspace():
                                                SrcPkgIdentifier = SrcPkgIdentifier.split(' ')[3].rstrip("\n")
                                                if SrcPkgIdentifier in SrcPkgDict[SrcPkgName]:
                                                        break
                                                else:
                                                        SrcPkgDict[SrcPkgName].append(SrcPkgIdentifier)
                                SrcPkgDict[SrcPkgName].append(filename)
                                temp.file.close()
                
                #if bug_parse_required is True:
                bugs_number = {}
                if Bool_SkipBugReports:
                        log.verbose("Skipping bug report check as requested")
                else:
                        for filename in file.namelist():
                                if filename.endswith( apt_bug_file_format ):
                                        temp = tempfile.NamedTemporaryFile()
                                        temp.file.write( file.read( filename ) )
                                        temp.file.flush()
                                        temp.file.seek( 0 ) #Let's go back to the start of the file
                                        for bug_subject_identifier in temp.file.readlines():
                                                if bug_subject_identifier.startswith( '#' ):
                                                        subject = bug_subject_identifier.lstrip( bug_subject_identifier.split( ":" )[0] )
                                                        subject = subject.rstrip( "\n" )
                                                        break
                                        bugs_number[filename] = subject
                                        temp.file.close()
                                        
                log.verbose(str(bugs_number) + "\n")
                if bugs_number:
                        # Display the list of bugs
                        list_bugs(bugs_number)
                        display_options()
                        response = get_response()
                        while True:
                                if response == "?":
                                        display_options()
                                        response = get_response()
                                elif response.startswith( 'y' ) or response.startswith( 'Y' ):
                                        for filename in file.namelist():
                                                
                                                #INFO: Take care of Src Pkgs
                                                found = False
                                                for item in SrcPkgDict.keys():
                                                        if filename in SrcPkgDict[item]:
                                                                found = True
                                                                break
                                                        
                                                data = tempfile.NamedTemporaryFile()
                                                data.file.write( file.read( filename ) )
                                                data.file.flush()
                                                archive_file = data.name
                                                
                                                if found is True:
                                                        shutil.copy2(archive_file, os.path.join(Str_InstallSrcPath, filename) )
                                                        log.msg("Installing src package file %s to %s.\n" % (filename, Str_InstallSrcPath) )
                                                        continue
                                                
                                                magic_check_and_uncompress( archive_file, filename )
                                                data.file.close()
                                        sys.exit( 0 )
                                elif response.startswith( 'n' ) or response.startswith( 'N' ):
                                        log.err( "Exiting gracefully on user request.\n\n" )
                                        sys.exit( 0 )
                                elif response.isdigit() is True:
                                        found = False
                                        for full_bug_file_name in bugs_number:
                                                if response in full_bug_file_name:
                                                        bug_file_to_display = full_bug_file_name
                                                        found = True
                                                        break
                                        if found == False:
                                                log.err( "Incorrect bug number %s provided.\n" % ( response ) )
                                                response = get_response()
                
                                        if found:
                                                display_pager = PagerCmd()
                                                retval = display_pager.send_to_pager( file.read( bug_file_to_display ) )
                                                if retval == 1:
                                                        log.err( "Broken pager. Can't display the bug details.\n" )
                                                # Redisplay the menu
                                                # FIXME: See a pythonic possibility of cleaning the screen at this stage
                                                response = get_response()
                
                                elif response.startswith( 'r' ) or response.startswith( 'R' ):
                                        list_bugs(bugs_number)
                                        response = get_response()
                                else:
                                        log.err( 'Incorrect choice. Exiting\n' )
                                        sys.exit( 1 )
                else:
                        log.verbose( "Great!!! No bugs found for all the packages that were downloaded.\n\n" )
                        #response = raw_input( "Continue with Installation. Y/N ?" )
                        #response = response.rstrip( "\r" )
                        #if response.endswith( 'y' ) or response.endswith( 'Y' ):
                        #        log.verbose( "Continuing with syncing the files.\n" )
                        for filename in file.namelist():
                                
                                #INFO: Take care of Src Pkgs
                                found = False
                                for item in SrcPkgDict.keys():
                                        if filename in SrcPkgDict[item]:
                                                found = True
                                                break
                                        
                                data = tempfile.NamedTemporaryFile()
                                data.file.write( file.read( filename ) )
                                data.file.flush()
                                archive_file = data.name
                                
                                if found is True:
                                        shutil.copy2(archive_file, os.path.join(Str_InstallSrcPath, filename) )
                                        log.msg("Installing src package file %s to %s.\n" % (filename, Str_InstallSrcPath) )
                                        continue
                                
                                magic_check_and_uncompress( archive_file, filename )
                                data.file.close()
                        #else:
                        #       log.msg( "Exiting gracefully on user request.\n" )
                        #       sys.exit( 0 )
                                
        elif os.path.isdir(install_file_path):
                
                SrcPkgDict = {}
                for filename in os.listdir( install_file_path ):
                        if filename.endswith(".dsc"):
                                SrcPkgName = filename.split('_')[0]
                                SrcPkgDict[SrcPkgName] = []
                                Tempfile = os.path.join(install_file_path, filename)
                                temp = open(Tempfile, 'r')
                                for SrcPkgIdentifier in temp.readlines():
                                        if SrcPkgIdentifier.startswith(' ') and not SrcPkgIdentifier.isspace():
                                                SrcPkgIdentifier = SrcPkgIdentifier.split(' ')[3].rstrip("\n")
                                                if SrcPkgIdentifier in SrcPkgDict[SrcPkgName]:
                                                        break
                                                else:
                                                        SrcPkgDict[SrcPkgName].append(SrcPkgIdentifier)
                                SrcPkgDict[SrcPkgName].append(filename)
                                temp.close()
                
                bugs_number = {}
                
                def DirInstallPackages(InstallDirPath):
                        for eachfile in os.listdir( InstallDirPath ):
                                
                                filename = eachfile
                                FullFileName = os.path.abspath(os.path.join(InstallDirPath, eachfile) )
                        
                                #INFO: Take care of Src Pkgs
                                found = False
                                for item in SrcPkgDict.keys():
                                        if filename in SrcPkgDict[item]:
                                                found = True
                                                break
                                if found is True:
                                        shutil.copy2(filename, Str_InstallSrcPath)
                                        log.msg("Installing src package file %s to %s.\n" % (filename, Str_InstallSrcPath) )
                                        continue
                                
                                magic_check_and_uncompress( FullFileName, filename )
                        return True
                                
                if Bool_SkipBugReports:
                        log.verbose("Skipping bug report check as requested")
                else:
                        for filename in os.listdir( install_file_path ):
                                if filename.endswith( apt_bug_file_format ):
                                        filename = os.path.join(install_file_path, filename)
                                        temp = open(filename, 'r')
                                        for bug_subject_identifier in temp.readlines():
                                                if bug_subject_identifier.startswith( '#' ):
                                                        subject = bug_subject_identifier.lstrip( bug_subject_identifier.split( ":" )[0] )
                                                        subject = subject.rstrip( "\n" )
                                                        break
                                        bugs_number[filename] = subject
                                        temp.close()
                log.verbose(str(bugs_number) + "\n")
                if bugs_number:
                        #Give the choice to the user
                        list_bugs(bugs_number)
                        display_options()
                        response = get_response()
                        
                        while True:
                                if response == "?":
                                        display_options()
                                        response = get_response()
                                        
                                elif response.startswith( 'y' ) or response.startswith( 'Y' ):
                                        if DirInstallPackages(install_file_path) is True:
                                                sys.exit(0)
                                        else:
                                                log.err("Failed during install operation on %s.\n" % (install_file_path) )
                                                sys.exit(1)
                                        
                                elif response.startswith( 'n' ) or response.startswith( 'N' ):
                                        log.err( "Exiting gracefully on user request.\n\n" )
                                        sys.exit( 0 )
                                        
                                elif response.isdigit() is True:
                                        found = False
                                        for full_bug_file_name in bugs_number:
                                                if response in full_bug_file_name:
                                                        bug_file_to_display = full_bug_file_name
                                                        found = True
                                                        break
                                        if found == False:
                                                log.err( "Incorrect bug number %s provided.\n" % ( response ) )
                                                response = get_response()
                                        if found:
                                                display_pager = PagerCmd()
                                                file = open(bug_file_to_display, 'r')
                                                retval = display_pager.send_to_pager(file.read())
                                                if retval == 1:
                                                        log.err( "Broken pager. Can't display the bug details.\n" )
                                                # Redisplay the menu
                                                # FIXME: See a pythonic possibility of cleaning the screen at this stage
                                                response = get_response()
                
                                elif response.startswith( 'r' ) or response.startswith( 'R' ):
                                        list_bugs(bugs_number)
                                        response = get_response()
                
                                else:
                                        log.err( 'Incorrect choice. Exiting\n' )
                                        sys.exit( 1 )
                else:
                        log.verbose( "Great!!! No bugs found for all the packages that were downloaded.\n\n" )
                        DirInstallPackages(install_file_path)
                        
        if Bool_Untrusted:
                log.err("Disabling apt gpg check can risk your machine to compromise.\n")
                for x in os.listdir(apt_update_target_path):
                        x = os.path.join(apt_update_target_path, x)
                        shutil.copy2(x, apt_update_final_path) # Do we do a move ??
                        log.verbose("%s %s\n" % (x, apt_update_final_path) )
                        log.msg("%s synced.\n" % (x) )
        else:
                lFileList= os.listdir(apt_update_target_path)
                lFileList.sort()
                lVerifiedWhitelist = []
                for file in lFileList:
                        file = os.path.join(apt_update_target_path, file)
                        if file.endswith('.gpg'):
                                log.verbose("%s\n" % (file) )
                                file = os.path.abspath(file)
                                if AptSecure.VerifySig(file, file.rstrip(".gpg") ):
                                        file = file.rstrip("Release.gpg")
                                        file = file[:-1] #Remove the trailing _ underscore
                                        file = file.split("/")[-1]
                                        lVerifiedWhitelist.append(file)
                                        log.verbose("%s is gpg clean\n" % (file) )
                                else:
                                        # Bad sig.
                                        log.err("%s bad signature. Not syncing because in strict mode.\n" % (file) )
                if lVerifiedWhitelist != []:
                        log.verbose (str(lVerifiedWhitelist) + "\n")
                        for whitelist_item in lVerifiedWhitelist:
                                for final_item in lFileList:
                                        if whitelist_item in final_item:
                                                final_item = os.path.join(apt_update_target_path, final_item)
                                                shutil.copy2(final_item, apt_update_final_path)
                                                log.msg("%s synced.\n" % (final_item) )
                        

def setter(args):
        log.verbose(str(args) )
        Str_SetArg = args.set
        List_SetInstallPackages = args.set_install_packages
        List_SetInstallSrcPackages = args.set_install_src_packages
        Str_SetInstallRelease = args.set_install_release
        Bool_SetUpdate = args.set_update
        Bool_SetUpgrade = args.set_upgrade
        Str_SetUpgradeType = args.upgrade_type
        Bool_SrcBuildDep = args.src_build_dep
        Bool_TestWindows = args.simulate
        
        if Bool_SetUpdate is False and Bool_SetUpgrade is False and List_SetInstallPackages is None \
        and List_SetInstallSrcPackages is None:
                Default_Operation = True
        else:
                Default_Operation = False
                
        #INFO: Don't run the default behavior, of SetUpdate and SetUpgrade, if the
        # user requests only for Package Installs
        if Default_Operation:
                Bool_SetUpdate = True
                Bool_SetUpgrade = True
                
        class AptManip:
                def __init__(self, OutputFile, Simulate=False, AptType="apt"):
                        
                        self.WriteTo = OutputFile
                        self.Simulate = Simulate
                        
                        if AptType == "apt":
                                self.apt = "apt-get"
                        elif AptType == "aptitude":
                                self.apt = "aptitude"
                        elif AptType == "python-apt":
                                #TODO:
                                pass
                        else:
                                self.apt = "apt-get"
                                
                def __Simulate(self):
                        if self.Simulate is True:
                                pass
                
                def __ExecSystemCmd(self, CommandString):
                        
                        if self.Simulate:
                                return True
                        else:
                                if os.system( CommandString ) != 0:
                                        return False
                                return True
                
                def Update(self):
                        if self.apt == "apt-get":
                                self.__AptGetUpdate()
                        elif self.apt == "aptitude":
                                pass
                        else:
                                log.err("Method not supported")
                                sys.exit(1)
                                
                                
                def Upgrade(self, UpgradeType="upgrade", ReleaseType=None):
                        if self.apt == "apt-get":
                                self.__AptGetUpgrade(UpgradeType, ReleaseType)
                        elif self.apt == "aptitude":
                                pass
                        else:
                                log.err("Method not supported")
                                sys.exit(1)
                
                def InstallPackages(self, PackageList, ReleaseType):
                        if self.apt == "apt-get":
                                self.__AptInstallPackage(PackageList, ReleaseType)
                        else:
                                log.err("Method not supported")
                                sys.exit(1)
                                
                def InstallSrcPackages(self, SrcPackageList, ReleaseType, BuildDependency):
                        if self.apt == "apt-get":
                                self.__AptInstallSrcPackages(SrcPackageList, ReleaseType, BuildDependency)
                        else:
                                log.err("Method not supported")
                                sys.exit(1)
                        
                        
                def __FixAptSigs(self):
                        for file in os.listdir(apt_update_target_path):
                                if file.endswith(".gpg.reverify"):
                                        sig_file = file.rstrip(".reverify")
                                        log.verbose("Recovering gpg signature %s.\n" % (file) )
                                        file = os.path.join(apt_update_target_path, file)
                                        os.rename(file, os.path.join(apt_update_final_path + sig_file) )
                                        
                                        
                def __AptGetUpdate(self):
                        log.msg("\nGenerating database of files that are needed for an update.\n")
                
                        #FIXME: Unicode Fix
                        # This is only a workaround.
                        # When using locales, we get translation files. But apt doesn't extract the URI properly.
                        # Once the extraction problem is root-caused, we can fix this easily.
                        os.environ['__apt_set_update'] = self.WriteTo
                        try:
                                old_environ = os.environ['LANG']
                        except KeyError:
                                old_environ = "C"
                        os.environ['LANG'] = "C"
                        log.verbose( "Set environment variable for LANG from %s to %s temporarily.\n" % ( old_environ, os.environ['LANG'] ) )
                        
                        if self.__ExecSystemCmd('/usr/bin/apt-get -qq --print-uris --simulate update >> $__apt_set_update') is False:
                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                        log.verbose( "Set environment variable for LANG back to its original from %s to %s.\n" % ( os.environ['LANG'], old_environ ) )
                        os.environ['LANG'] = old_environ
                        
                        log.verbose("Calling __FixAptSigs to fix the apt sig problem")
                        self.__FixAptSigs()
                                
                def __AptitudeUpdate(self):
                        pass
                
                def __PythonAptUpdate(self):
                        pass
                
                def __AptGetUpgrade(self, UpgradeType="upgrade", ReleaseType=None):
                        self.ReleaseType = ReleaseType
                        
                        os.environ['__apt_set_upgrade'] = self.WriteTo
                        
                        if ReleaseType is not None:
                                os.environ['__apt_set_install_release'] = self.ReleaseType
                                if UpgradeType == "upgrade":
                                        log.msg( "\nGenerating database of files that are needed for an upgrade.\n" )
                                        
                                        if self.__ExecSystemCmd('/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release upgrade >> $__apt_set_upgrade') is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                                        
                                elif Str_SetUpgradeType == "dist-upgrade":
                                        log.msg( "\nGenerating database of files that are needed for a dist-upgrade.\n" )
                                        
                                        if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release dist-upgrade >> $__apt_set_upgrade' ) is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                                
                                elif Str_SetUpgradeType == "dselect-upgrade":
                                        log.msg( "\nGenerating database of files that are needed for a dselect-upgrade.\n" )
                                        if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release dselect-upgrade >> $__apt_set_upgrade' )  is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                else:
                                        log.err( "Invalid upgrade argument type selected\nPlease use one of, upgrade/dist-upgrade/dselect-upgrade\n" )
                                        
                        else:
                                
                                if UpgradeType == "upgrade":
                                        log.msg( "\nGenerating database of files that are needed for an upgrade.\n" )
                                        
                                        if self.__ExecSystemCmd('/usr/bin/apt-get -qq --print-uris upgrade >> $__apt_set_upgrade') is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                                        
                                elif Str_SetUpgradeType == "dist-upgrade":
                                        log.msg( "\nGenerating database of files that are needed for a dist-upgrade.\n" )
                                        
                                        if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris dist-upgrade >> $__apt_set_upgrade' ) is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                                
                                elif Str_SetUpgradeType == "dselect-upgrade":
                                        log.msg( "\nGenerating database of files that are needed for a dselect-upgrade.\n" )
                                        if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris dselect-upgrade >> $__apt_set_upgrade' )  is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                else:
                                        log.err( "Invalid upgrade argument type selected\nPlease use one of, upgrade/dist-upgrade/dselect-upgrade\n" )
                                
                def __AptInstallPackage(self, PackageList=None, ReleaseType=None):
                        
                        self.package_list = ''
                        self.ReleaseType = ReleaseType
                        
                        for pkg in PackageList:
                                self.package_list += pkg + ', '
                        log.msg( "\nGenerating database of package %s and its dependencies.\n" % (self.package_list) )
                        
                        os.environ['__apt_set_install'] = self.WriteTo
                        os.environ['__apt_set_install_packages'] = ''                   # Build an empty variable
        
                        #INFO: This is improper way of getting the args, the name of the packages.
                        # But since optparse doesn't have the implementation in place at the moment, we're using it.
                        # Once fixed, this will be changed.
                        # For details look at the parser.add_option line above.
                        for x in PackageList:
                                os.environ['__apt_set_install_packages'] += x + ' '
                        
                        if self.ReleaseType is not None:
                                os.environ['__apt_set_install_release'] = self.ReleaseType
                                if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release install $__apt_set_install_packages >> $__apt_set_install' ) is False:
                                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                        else:
                                #FIXME: Find a more Pythonic implementation
                                if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris install $__apt_set_install_packages >> $__apt_set_install' ) is False:
                                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                                        
                def __AptInstallSrcPackages(self, SrcPackageList=None, ReleaseType=None, BuildDependency=False):
                        
                        self.package_list = ''
                        self.ReleaseType = ReleaseType
                        
                        for pkg in SrcPackageList:
                                self.package_list += pkg + ', '
                        log.msg( "\nGenerating database of source packages %s.\n" % (self.package_list) )
                        
                        os.environ['__apt_set_install'] = self.WriteTo
                        os.environ['__apt_set_install_src_packages'] = ''               # Build an empty variable
                        
                        for x in SrcPackageList:
                                os.environ['__apt_set_install_src_packages'] += x + ' '
                                
                        if self.ReleaseType is not None:
                                os.environ['__apt_set_install_release'] = self.ReleaseType
                                if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release source $__apt_set_install_src_packages >> $__apt_set_install' ) is False:
                                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                        else:
                                #FIXME: Find a more Pythonic implementation
                                if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris source $__apt_set_install_src_packages >> $__apt_set_install' )  is False:
                                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                        
                        if BuildDependency:
                                log.msg("Generating Build-Dependency for source packages %s.\n" % (self.package_list) )
                                if self.ReleaseType is not None:
                                        os.environ['__apt_set_install_release'] = self.ReleaseType
                                        if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release build-dep $__apt_set_install_src_packages >> $__apt_set_install' ) is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                else:
                                        if self.__ExecSystemCmd( '/usr/bin/apt-get -qq --print-uris build-dep $__apt_set_install_src_packages >> $__apt_set_install' ) is False:
                                                log.err( "FATAL: Something is wrong with the apt system.\n" )
                                
                
                                
        #FIXME: We'll use python-apt library to make it cleaner.
        # For now, we need to set markers using shell variables.
        if os.path.isfile(Str_SetArg):
                try:
                        os.unlink(Str_SetArg)
                except OSError:
                        log.err("Cannot remove file %s.\n" % (Str_SetArg) )
        
        
        #Instantiate Apt based on what we have. For now, fall to apt only
        AptInst = AptManip(Str_SetArg, Simulate=Bool_TestWindows, AptType="apt")
        
        if Bool_SetUpdate:
                if platform.system() in supported_platforms:
                        if not Bool_TestWindows and os.geteuid() != 0:
                                log.err("This option requires super-user privileges. Execute as root or use sudo/su\n")
                                sys.exit(1)
                        else:
                                AptInst.Update()
                else:
                        log.err( "This argument is supported only on Unix like systems with apt installed\n" )
                        sys.exit( 1 )
                        
        if Bool_SetUpgrade:
                if platform.system() in supported_platforms:
                        if not Bool_TestWindows and os.geteuid() != 0:
                                log.err( "This option requires super-user privileges. Execute as root or use sudo/su" )
                                sys.exit(1)
                        #TODO: Use a more Pythonic way for it
                        if Str_SetUpgradeType == "upgrade":
                                if PythonApt is True:
                                        #FIXME: Adapt the new python-apt. Ideas from debdelta
                                        log.verbose("Using the python-apt library to generate the database.\n")
                                        PythonAptQuery = AptPython()
                                        try:
                                                install_file = open( Str_SetArg, 'a' )
                                        except IOError:
                                                log.err( "Cannot create file %s.\n" % (Str_SetArg) )
                                                sys.exit( 1 )
                                        upgradable = filter( lambda p: p.isUpgradable, PythonAptQuery.cache )
                                        log.msg( "\nGenerating database of files that are needed for an upgrade.\n" )
                                        
                                        dup_records = []
                                        for pkg in upgradable:
                                                pkg._lookupRecord( True )
                                                dpkg_params = apt_pkg.ParseSection(pkg._records.Record)
                                                arch = dpkg_params['Architecture']
                                                path = dpkg_params['Filename']
                                                checksum = dpkg_params['SHA256'] #FIXME: There can be multiple checksum types
                                                size = dpkg_params['Size']
                                                cand = pkg._depcache.GetCandidateVer( pkg._pkg )
                                                for ( packagefile, i ) in cand.FileList:
                                                        indexfile = PythonAptQuery.cache._list.FindIndex( packagefile )
                                                        if indexfile:
                                                                uri = indexfile.ArchiveURI( path )
                                                                file = uri.split( '/' )[ - 1]
                                                                if checksum.__str__() in dup_records:
                                                                        continue
                                                                install_file.write( uri + ' ' + file + ' ' + size + ' ' + checksum + "\n" )
                                                                dup_records.append( checksum.__str__() )
                                else:
                                        AptInst.Upgrade("upgrade", ReleaseType=Str_SetInstallRelease)
                        elif Str_SetUpgradeType == "dist-upgrade":
                                AptInst.Upgrade("dist-upgrade")
                        elif Str_SetUpgradeType == "dselect-upgrade":
                                AptInst.Upgrade("dselect-upgrade")
                        else:
                                log.err( "Invalid upgrade argument type selected\nPlease use one of, upgrade/dist-upgrade/dselect-upgrade\n" )
                else:
                        log.err( "This argument is supported only on Unix like systems with apt installed\n" )
                        sys.exit( 1 )
                
        if List_SetInstallPackages != None and List_SetInstallPackages != []:
                if platform.system() in supported_platforms:
                        if not Bool_TestWindows and os.geteuid() != 0:
                                log.err( "This option requires super-user privileges. Execute as root or use sudo/su\n" )
                                sys.exit(1)
                                
                        AptInst.InstallPackages(List_SetInstallPackages, Str_SetInstallRelease)
                else:
                        log.err( "This argument is supported only on Unix like systems with apt installed\n" )
                        sys.exit( 1 )
        
        if List_SetInstallSrcPackages != None and List_SetInstallSrcPackages != []:
                if platform.system() in supported_platforms:
                        AptInst.InstallSrcPackages(List_SetInstallSrcPackages, Str_SetInstallRelease, Bool_SrcBuildDep)
                else:
                        log.err( "This argument is supported only on Unix like systems with apt installed\n" )
                        sys.exit( 1 )
        
def gui(args):
        Bool_GUI = args.gui
        log.msg("Graphical Interface is currently not ready.\n")
        if Bool_GUI:
                if guiBool is True:
                        class GUI( pyptofflineguiForm ):
                                pass
                        app = QApplication( sys.argv )
                        QObject.connect( app, SIGNAL( "lastWindowClosed()" ), app, SLOT( "quit()" ) )
                        w = GUI()
                        app.setMainWidget( w )
                        w.show()
                        app.exec_loop()
                else:
                        log.err( "Incomplete installation. PyQT or apt-offline GUI libraries not available.\n" )
                        sys.exit( 1 )
        
class AptPython:
        def __init__( self ):
                if PythonApt:
                        self.cache = apt.Cache()
                
def main():
        '''Here we basically do the sanity checks, some validations
        and then accordingly call the corresponding functions.
        
        Contains most of the variables that are required by the application to run.
        Also does command-line option parsing and variable validation.'''
        
        # INFO: One way to handle global options in argparse so that they are available to 
        # subparsers also
        
        # Global options
        global_options = argparse.ArgumentParser(add_help=False)
        global_options.add_argument("--verbose", dest="verbose", help="Enable verbose messages", action="store_true" )
        global_options.add_argument("--simulate", dest="simulate", help="Just simulate. Very helpful when debugging",
                            action="store_true" )
        
        parser = argparse.ArgumentParser( prog=app_name, description="Offline APT Package Manager" + ' - ' + version,
                                          epilog=copyright + " - " + terminal_license, parents=[global_options])
        parser.add_argument("-v", "--version", action='version', version=version)
        
        # We need subparsers for set/get/install
        subparsers = parser.add_subparsers()
        
        # SET command options
        #
        parser_set = subparsers.add_parser('set', parents=[global_options])
        parser_set.set_defaults(func=setter)
        
        parser_set.add_argument('set',
                          help="Generate a signature file",
                          action="store", type=str, metavar="apt-offline.sig",
                          default="apt-offline.sig")
        
        #TODO: Handle nargs here.
        parser_set.add_argument("--install-packages", dest="set_install_packages", help="Packages that need to be installed",
                          action="store", type=str, nargs='*', metavar="PKG")
        
        parser_set.add_argument("--install-src-packages", dest="set_install_src_packages", help="Source Packages that need to be installed",
                          action="store", type=str, nargs='*', metavar="SOURCE PKG")
        
        parser_set.add_argument("--src-build-dep", dest="src_build_dep", help="Install Build Dependency packages for requested source packages",
                                action="store_true")
        
        parser_set.add_argument("--release", dest="set_install_release", help="Release target to install packages from",
                          action="store", type=str, metavar="release_name" )
        
        parser_set.add_argument("--update", dest="set_update", help="Generate Signature to update APT Database",
                          action="store_true")
        
        parser_set.add_argument("--upgrade", dest="set_upgrade", help="Generate Signature of packages to be upgraded",
                          action="store_true")
        
        parser_set.add_argument("--upgrade-type", dest="upgrade_type",
                          help="Type of upgrade to do. Use one of upgrade, dist-upgrade, dselect-ugprade",
                          action="store", type=str, metavar="upgrade", default="upgrade")
        
        
        # GET command options
        parser_get = subparsers.add_parser('get', parents=[global_options])
        
        #INFO: When get option is called, call the fetcher() function
        parser_get.set_defaults(func=fetcher)
        
        parser_get.add_argument('get',
                          help="Get apt-offline data",
                          action="store", type=str, metavar="apt-offline.sig",
                          default="apt-offline.sig")
        
        parser_get.add_argument("--socket-timeout", dest="socket_timeout", help="Set Socket Timeout",
                        action="store", type=int, metavar="30", default=30)
        
        parser_get.add_argument("-d", "--download-dir", dest="download_dir",
                          help="Folder path to save files to", action="store",
                          type=str, metavar="apt-downloads")
        
        parser_get.add_argument("-s", "--cache-dir", dest="cache_dir",
                          help="Cache folder to search for",
                          action="store", type=str, metavar=".")
        
        parser_get.add_argument("--no-checksum", dest="disable_md5check",
                          help="Do not validate checksum of downloaded files",
                          action="store_true")
        
        parser_get.add_argument("-t", "--threads", dest="num_of_threads", help="Number of threads to spawn",
                          action="store", type=int, metavar="1", default=1 )
        
        parser_get.add_argument("--bundle", dest="bundle_file", help="Bundle output data to a file",
                                action="store", type=str, metavar="apt-offline-bundle.zip")
        
        parser_get.add_argument("--bug-reports", dest="deb_bugs",
                          help="Fetch bug reports from the BTS", action="store_true" )
        
        # INSTALL command options
        parser_install = subparsers.add_parser('install', parents=[global_options])
        parser_install.set_defaults(func=installer)
        
        parser_install.add_argument('install',
                          help="Install apt-offline data, a bundle file or a directory",
                          action="store", type=str, metavar="apt-offline-download.zip | apt-offline-download/")

        parser_install.add_argument("--install-src-path", dest="install_src_path",
                                    help="Install src packages to specified path.", default=None)
        
        parser_install.add_argument("--skip-bug-reports", dest="skip_bug_reports",
                        help="Skip the bug report check", action="store_true")
        
        parser_install.add_argument("--allow-unauthenticated", dest="allow_unauthenticated",
                                    help="Ignore apt gpg signatures mismatch", action="store_true")
        
        # GUI options
        parser_gui = subparsers.add_parser('gui', parents=[global_options])
        parser_gui.set_defaults(func=gui)
        parser_gui.add_argument('gui', help="Run apt-offline in Graphical mode", action="store_true")
        
        args = parser.parse_args()
        
        try:
                # Sanitize the options/arguments
                #
        	# Global opts
        	Bool_Verbose = args.verbose
        	Bool_TestWindows = args.simulate
                
        	global log
        	log = AptOfflineLib.Log( Bool_Verbose, lock=True )
        	log.verbose(str(args) + "\n")
        
        	args.func(args)
            
        except KeyboardInterrupt:
                log.err("\nInterrupted by user. Exiting!\n")
                sys.exit(0)        
