
############################################################################
#    Copyright (C) 2005, 2015 Ritesh Raj Sarraf                            #
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
import time
import shutil
import platform
import string
import ssl
import urllib2
import httplib
import Queue
import threading
import subprocess
import shlex
import socket
import tempfile
import random   # to generate random directory names for installing multiple bundles in on go
import zipfile
import pydoc

FCNTL_LOCK = True
try:
        import fcntl
except ImportError:
        # Only available on platform Unix
        FCNTL_LOCK = False
                
# Given the merits of argparse, I hope it'll soon be part
# of the Python Standard Library.
# http://code.google.com/argparse
# Till then we use it this way.
try:
        import argparse
except ImportError:
        from apt_offline_core import AptOffline_argparse as argparse

# On Debian, python-debianbts package provides this library
DebianBTS = True
try:
        import debianbts
except ImportError:
        try:
                from apt_offline_core import AptOfflineDebianBtsLib as debianbts
        except ImportError:
                DebianBTS = False

try:
        MagicLib = True
        from apt_offline_core import AptOfflineMagicLib
except TypeError:
        ''' On Windows, the file magic library does not work '''
        MagicLib = False
except AttributeError:
        # On Linux, make sure libmagic is installed
        MagicLib = False


#INFO: added to handle GUI interaction
guiBool = False
guiTerminateSignal = False     # cancelling a download
guiMetaCompleted = False
totalSize = [0,0]              # total_size, current_total

#INFO: Check if python-apt is installed
PythonApt = True
try:
        import apt
        import apt_pkg
except ImportError:
        PythonApt = False

# Completely disable python-apt
PythonApt = False
    
from apt_offline_core import AptOfflineLib

#INFO: Set the default timeout to 30 seconds for the packages that are being downloaded.
socket.setdefaulttimeout(30)

# How many times should we retry on socket timeouts
SOCKET_TIMEOUT_RETRY = 5

'''This is the core module. It does the main job of downloading packages/update packages,\n
figuring out if the packages are in the local cache, handling exceptions and many more stuff'''


app_name = "apt-offline"
version = "1.7"
myCopyright = "(C) 2005 - 2015 Ritesh Raj Sarraf"
terminal_license = "This program comes with ABSOLUTELY NO WARRANTY.\n\
This is free software, and you are welcome to redistribute it under\n\
the GNU GPL Version 3 (or later) License\n"
        
errlist = []
supported_platforms = ["Linux", "GNU/kFreeBSD", "GNU"]
apt_update_target_path = '/var/lib/apt/lists/partial'
apt_update_final_path = '/var/lib/apt/lists/'
apt_package_target_path = '/var/cache/apt/archives/'

# Locks
apt_lists_lock = '/var/lib/apt/lists/lock'
apt_packages_lock = '/var/cache/apt/archives/lock'

apt_bug_file_format = "__apt__bug__report"
IgnoredBugTypes = ["Resolved bugs", "Normal bugs", "Minor bugs", "Wishlist items", "FIXED"]


#These are spaces which will overwrite the progressbar left mess
LINE_OVERWRITE_SMALL = " " * 10
LINE_OVERWRITE_MID = " " * 30
LINE_OVERWRITE_FULL = " " * 60

Bool_Verbose = False
#Bool_TestWindows = True
                
log = AptOfflineLib.Log( Bool_Verbose, lock=True )

       
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
                        #( num_of_bugs, header, self.bugs_list ) = debianbts.get_bugs( 'package', PackageName )
                        self.bugs_list = debianbts.get_bugs( 'package', PackageName )
                        num_of_bugs = len(self.bugs_list)
                except socket.timeout:
                        return 0
                        
                
                if num_of_bugs:
                        atleast_one_bug_report_downloaded = False
                        for eachBug in self.bugs_list:
                                
                                # Fetch bug report..
                                # TODO: Handle exceptions later
                                bugReport = debianbts.get_bug_log(eachBug)
                                
                                # This tells us how many follow-ups for the bug report are present.
                                bugReportLength = bugReport.__len__()
                                writeBugReport = 0
                                
                                if Filename == None:
                                        #INFO: '{}' is the bug split identifier - Used at other places also
                                        self.fileName = PackageName + "{}" + str(eachBug) + "{}" + self.apt_bug
                                        file_handle = open( self.fileName, 'w' )
                                else:
                                        self.fileName = Filename
                                        file_handle = open( self.fileName, 'a' )
            
                                #TODO: Can we manipulate these headers in a more efficient way???
                                for line in bugReport[writeBugReport]['header'].encode('utf8').split("\n"):
                                        if line.startswith("Subject:"):
                                                file_handle.write(line)
                                                file_handle.write("\n")
                                                break
                                    
                                while writeBugReport < bugReportLength:
                                        file_handle.write(bugReport[writeBugReport]['body'].encode('utf8'))
                                        file_handle.write("\n\n".encode('utf8'))
                                        writeBugReport += 1
                                        if writeBugReport < bugReportLength:
                                                file_handle.write("Follow-Up #%d\n\n".encode('utf8') % writeBugReport)
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
        
class ExecCmd:
        def __init__(self, Simulate=False):
                self.Simulate = Simulate

        def Simulate(self):
                if self.Simulate is True:
                        pass
        
        def ExecSystemCmd(self, cmd, sigFile=None):
                if self.Simulate:
                        return True
                
                if sigFile is None: #subprocess.call does take None as an arg
                        fh = None
                else:
                        try:
                                fh = open(sigFile, 'a')
                        except:
                                return False
                
                if fh is not None:
                        preState = fh.tell()

                log.verbose("Command is: %s\n" % (cmd))
                
                p = subprocess.call(cmd, universal_newlines=True, stdout=fh)
                if fh is not None:
                        fh.flush()

                if p != 0:
                        #INFO: stderr will give us junk which our stripper() will not understand
                        # So, under that condition, truncate the data so that at least, our
                        # sig file is still usable
                        if fh is not None:
                                fh.truncate(preState)
                                fh.flush()
                        return False
                return True
                
class AptManip(ExecCmd):
        def __init__(self, OutputFile, Simulate=False, AptType="apt", AptReinstall=False):
                
                ExecCmd.__init__(self, Simulate)
                self.WriteTo = OutputFile
                self.AptReinstall = AptReinstall
                
                if AptType == "apt":
                        self.apt = "apt-get"
                elif AptType == "aptitude":
                        self.apt = "aptitude"
                elif AptType == "python-apt":
                        self.apt = "python-apt"
                else:
                        self.apt = "apt-get"
                        
        
        def Update(self):
                log.verbose("APT Update Method is of type: %s\n" % self.apt)
                if self.apt == "apt-get":
                        self.__AptGetUpdate()
                elif self.apt == "aptitude":
                        pass
                elif self.apt == "python-apt":
                        self.__PythonAptUpdate()
                else:
                        log.err("Method not supported")
                        sys.exit(1)
                        
                        
        def Upgrade(self, UpgradeType="upgrade", ReleaseType=None):
                log.verbose("APT Upgrade Method is of type: %s\n" % self.apt)
                if self.apt == "apt-get":
                        self.__AptGetUpgrade(UpgradeType, ReleaseType)
                elif self.apt == "aptitude":
                        pass
                elif self.apt == "python-apt":
                        # Upgrade is broken in python-apt
                        # Hence for now, redirect to apt-get
                        self.__AptGetUpgrade(UpgradeType, ReleaseType)
                else:
                        log.err("Method not supported")
                        sys.exit(1)
        
        def InstallPackages(self, PackageList, ReleaseType):
                log.verbose("APT Install Method is of type: %s\n" % self.apt)
                if self.apt == "apt-get":
                        self.__AptInstallPackage(PackageList, ReleaseType)
                elif self.apt == "python-apt":
                        self.__AptInstallPackage(PackageList, ReleaseType)
                else:
                        log.err("Method not supported")
                        sys.exit(1)
                        
        def InstallSrcPackages(self, SrcPackageList, ReleaseType, BuildDependency):
                log.verbose("APT Install Source Method is of type: %s\n" % self.apt)
                if self.apt == "apt-get":
                        self.__AptInstallSrcPackages(SrcPackageList, ReleaseType, BuildDependency)
                elif self.apt == "python-apt":
                        self.__AptInstallSrcPackages(SrcPackageList, ReleaseType, BuildDependency)
                else:
                        log.err("Method not supported")
                        sys.exit(1)
                
                
        def __FixAptSigs(self):
                for localFile in os.listdir(apt_update_target_path):
                        if localFile.endswith(".gpg.reverify"):
                                sig_file = localFile.rstrip(".reverify")
                                log.verbose("Recovering gpg signature %s.\n" % (localFile) )
                                localFile = os.path.join(apt_update_target_path, localFile)
                                os.rename(localFile, os.path.join(apt_update_final_path + sig_file) )
                                
                                
        def __AptGetUpdate(self):
                log.msg("\nGenerating database of files that are needed for an update.\n")
                if self.ExecSystemCmd(["/usr/bin/apt-get", "-q", "--print-uris", "update"], self.WriteTo) is False:
                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                log.verbose("Calling __FixAptSigs to fix the apt sig problem")
                self.__FixAptSigs()
                        
        def __AptitudeUpdate(self):
                pass
        
        def __PythonAptUpdate(self):
                log.verbose("Open file %s for write" % self.WriteTo)
                try:
                        writeFH = open(self.WriteTo, 'a')
                except:
                        log.err("Failed to open file %s for write. Exiting\n" % (self.WriteTo))
                        sys.exit(1)
                
                log.msg("\nGenerating database of files that are needed for an update.\n")
                log.verbose("\nUsing python apt interface\n")
                
                apt_pkg.init_config()
                apt_pkg.init_system()
                
                acquire = apt_pkg.Acquire()
                slist = apt_pkg.SourceList()
                
                # Read the main list
                slist.read_main_list()
                
                # Add all indexes to the fetcher
                slist.get_indexes(acquire, True)
                
                # Now write the URI of every item
                for item in acquire.items:
                        
                        #INFO: For update files, there's no checksum present.
                        # Also, their size is not determined.
                        # Hence filesize is always returned '0'
                        # And checksum is something I'm writing as ':'
                        
                        # We strip item.destfile because that's how apt-get had historically presented it to us
                        destFile = item.destfile.split("/")[-1]

                        writeFH.write("'" + item.desc_uri + "'" + " " + destFile + " " + str(item.filesize) + " " + ":" + "\n")
                        log.verbose("Writing string %s %s %d %s to file %s\n" % (item.desc_uri, destFile, item.filesize, ":", self.WriteTo) )
                        writeFH.flush()
                writeFH.close()
        
        def __PythonAptUpgrade(self, UpgradeType="upgrade", ReleaseType=None):
                
                log.verbose("Open file %s for write" % self.WriteTo)
                try:
                        writeFH = open(self.WriteTo, 'a')
                except:
                        log.err("Failed to open file %s for write. Exiting")
                        sys.exit(1)
                
                log.msg("\nGenerating database of files that are needed for an upgrade.\n")
                log.verbose("\nUsing python apt interface\n")
                
                #TODO: Right now, I don't know what to do with UpgradeType and Release Type in python-apt
                cache = apt.Cache()
                upgradablePkgs = filter(lambda p: p.is_upgradable, cache)
                
                for pkg in upgradablePkgs:
                        pkg._lookupRecord(True)
                        path = apt_pkg.TagSection(pkg._records.record)["Filename"]
                        cand = pkg._depcache.get_candidate_ver(pkg._pkg)
                        
                        for (packagefile, i) in cand.file_list:
                                indexfile = cache._list.find_index(packagefile)
                                if indexfile:
                                        uri = indexfile.archive_uri(path)
                                        print uri

        def __AptGetUpgrade(self, UpgradeType="upgrade", ReleaseType=None):
                self.ReleaseType = ReleaseType
                
                if ReleaseType is not None:
                        cmd = ["/usr/bin/apt-get", "-qq", "--print-uris", "-t"]
                        cmd.append(self.ReleaseType)
                        cmd.append(UpgradeType)
                else:
                        cmd = ["/usr/bin/apt-get", "-qq", "--print-uris"]
                        cmd.append(UpgradeType)

                log.msg("\nGenerating database of file that are needed for operation %s\n" % (UpgradeType) )
                if self.ExecSystemCmd(cmd, self.WriteTo) is False:
                        log.err("FATAL: Something is wrong with the APT system\n")
                        
        def __AptInstallPackage(self, PackageList=None, ReleaseType=None):

                self.ReleaseType = ReleaseType

                log.msg( "\nGenerating database of package %s and its dependencies.\n" % (PackageList) )

                if self.ReleaseType is not None:
                        cmd = ["/usr/bin/apt-get", "-qq", "--print-uris", "install", "-t"]
                        cmd.append(self.ReleaseType)
                else:
                        cmd = ["/usr/bin/apt-get", "-qq", "--print-uris", "install"]

                for pkg in PackageList:
                        cmd.append(pkg)

                if self.ExecSystemCmd(cmd, self.WriteTo) is False:
                        log.err( "FATAL: Something is wrong with the apt system.\n" )

        def __AptInstallSrcPackages(self, SrcPackageList=None, ReleaseType=None, BuildDependency=False):
                
                self.ReleaseType = ReleaseType
                
                log.msg( "\nGenerating database of source packages %s.\n" % (SrcPackageList) )
                
                if self.ReleaseType is not None:
                        cmd = ["/usr/bin/apt-get", "-qq", "--print-uris", "source", "-t"]
                        cmd.append(self.ReleaseType)
                        cmdBuildDep = ["/usr/bin/apt-get", "-qq", "--print-uris", "build-dep", "-t"]
                        cmdBuildDep.append(self.ReleaseType)
                else:
                        cmd = ["/usr/bin/apt-get", "-qq", "--print-uris", "source"]
                        cmdBuildDep = ["/usr/bin/apt-get", "-qq", "--print-uris", "build-dep"]

                for pkg in SrcPackageList:
                        cmd.append(pkg)
                        cmdBuildDep.append(pkg)
                
                if self.ExecSystemCmd(cmd, self.WriteTo) is False:
                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                if BuildDependency:
                        log.msg("Generating Build-Dependency for source packages %s.\n" % (SrcPackageList) )
                        if self.ExecSystemCmd(cmdBuildDep, self.WriteTo) is False:
                                log.err( "FATAL: Something is wrong with the apt system.\n" )
        


class APTVerifySigs(ExecCmd):
        
        def __init__(self, gpgv=None, keyring=None, Simulate=False):
                
                ExecCmd.__init__(self, Simulate)
                self.defaultPaths = ['/etc/apt/trusted.gpg.d/', '/usr/share/keyrings/']

                if gpgv is None:
                        self.gpgv="/usr/bin/gpgv"
                else:
                        self.gpgv=gpgv
                
                self.opts = []        
                if keyring is None:
                        
                        self.opts.append("--ignore-time-conflict")
                        
                        #INFO: For backwards compatibility
                        if os.path.exists("/etc/apt/trusted.gpg"):
                                self.opts.extend("--keyring /etc/apt/trusted.gpg".split())

                        for eachPath in self.defaultPaths:
                                if os.path.exists(eachPath):
                                        for eachGPG in os.listdir(eachPath):
                                                eachGPG = os.path.join(eachPath, eachGPG)
                                                if os.path.exists(eachGPG):
                                                        log.verbose("Adding %s to the apt-offline keyring\n" % (eachGPG) )
                                                        eachKeyring = "--keyring %s" % (eachGPG)
                                                        self.opts.extend(eachKeyring.split())
                                                else:
                                                        log.err("Path for keyring is invalid: %s\n" % (eachGPG) )
                                else:
                                        log.err("Path for keyring is invalid: %s\n" % (eachPath) )
                else:
                        finalKeyring = "--keyring %s --ignore-time-conflict" % (keyring)
                        self.opts.extend(finalKeyring.split())
                        
        def VerifySig(self, signature_file, signed_file):
                
                if not os.access(signature_file, os.F_OK):
                        log.err("%s is bad. Can't proceed.\n" % (signature_file) )
                        return False
                if not os.access(signed_file, os.F_OK):
                        log.err("%s is bad. Can't proceed.\n" % (signed_file) )
                        return False
                
                #INFO: Commands can escape and inject. So carefully craft the command
                # Thanks: Bernd Dietzel
                gpgvCmd = []
                gpgvCmd.append(self.gpgv)
                gpgvCmd.extend(self.opts)
                gpgvCmd.append(signature_file)
                gpgvCmd.append(signed_file)
                return self.ExecSystemCmd(gpgvCmd, None)
        

class LockAPT:
        '''Manipulate locks on the APT Database'''
        
        def __init__(self, lists, packages):
                
                try:
                        self.listLock = os.open(lists, os.O_RDWR | os.O_TRUNC | os.O_CREAT, 0640)
                        self.pkgLock = os.open(packages, os.O_RDWR | os.O_TRUNC | os.O_CREAT, 0640)
                except:
                        log.err("Couldn't open lockfile\n")
                        return False
                        
        def lockLists(self):
                try:
                        fcntl.lockf(self.listLock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        return True
                except:
                        return False
                
        def lockPackages(self):
                try:
                        fcntl.lockf(self.pkgLock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        return True
                except:
                        return False
                
        def unlockLists(self):
                try:
                        fcntl.lockf(self.listLock, fcntl.LOCK_UN)
                        return True
                except:
                        return False
        
        def unlockPackages(self):
                try:
                        fcntl.lockf(self.pkgLock, fcntl.LOCK_UN)
                        return True
                except:
                        return False

        
def files(root): 
        for path, folders, files in os.walk(root): 
                for localFile in files:
                        yield path, localFile
    
    
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
                for path, localFile in files(cache_dir):
                        if localFile == filename:
                                return os.path.join(path, localFile)
                return False
        

class GenericDownloadFunction():
        def download_from_web(self, url, localFile, download_dir):
                '''url = url to fetch
                localFile = file to save to
                donwload_dir = download path'''
                try:
                        block_size = 4096
                        i = 0
                        counter = 0
                        
                        os.chdir(download_dir)
                        temp = urllib2.urlopen(url)
                        headers = temp.info()
                        size = int(headers['Content-Length'])
                        data = open(localFile,'wb')
            
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
                                        os.unlink(localFile)
                                        return False
                                
                                if socket_timeout is True:
                                        errfunc(10054, "Socket Timeout. Retry - %d\n" % (socket_counter) , url)
                                        continue
                
                                increment = min(block_size, size - i)
                                i += block_size
                                counter += 1
                                self.updateValue(increment)
                                #REAL_PROGRESS: update current total in totalSize
                                if guiBool and not guiTerminateSignal:
                                        totalSize[1] += block_size
                                if guiTerminateSignal:
                                        data.close()
                                        temp.close()
                                        return False
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
                except httplib.BadStatusLine:
                        #INFO: See Python Bug: https://bugs.python.org/issue8823
                        log.err("BadStatusLine exception: Python Bug 8823")
                except IOError, e:
                        if hasattr(e, 'reason'):
                                log.err("%s\n" % (e.reason))
                        if hasattr(e, 'code') and hasattr(e, 'reason'):
                                errfunc(e.code, e.reason, localFile)
                except socket.timeout:
                        errfunc(10054, "Socket timeout.\n", url)
     
class DownloadFromWeb(AptOfflineLib.ProgressBar, GenericDownloadFunction):
        '''Class for DownloadFromWeb
        This class also inherits progressbar functionalities from
        parent class, ProgressBar'''
        
        def __init__(self, width, total_items):
                '''width = Progress Bar width'''
                AptOfflineLib.ProgressBar.__init__(self, width=width, total_items=total_items)
        

def stripper(item):
        '''Strips extra characters from "item".
        Breaks "item" into:
        url - The URL
        localFile - The actual package file
        size - The file size
        checksum - The checksum string
        and returns them.'''
    
        item = item.split(' ')
        log.verbose("Item is %s\n" % (item) )

        url = string.rstrip(string.lstrip(''.join(item[0]), chars="'"), chars="'")
        log.verbose("Stripped item URL is: %s\n" % url)
        
        localFile = string.rstrip(string.lstrip(''.join(item[1]), chars="'"), chars="'")
        log.verbose("Stripped item FILE is: %s\n" % localFile)
        
        try:
                size = int(string.rstrip(string.lstrip(''.join(item[2]), chars = "'"), chars="'"))
        except ValueError:
                log.verbose("%s is malformed\n" % (" ".join(item) ) )
                size = 0
        log.verbose("Stripped item SIZE is: %d\n" % size)
        

        #INFO: md5 ends up having '\n' with it.
        # That needs to be stripped too.
        try:
                checksum = string.rstrip(string.lstrip(''.join(item[3]), chars = "'"), chars = "'")
                checksum = string.rstrip(checksum, chars = "\n")
        except IndexError:
                if item[1].endswith("_Release") or item[1].endswith("_Release.gpg"):
                        checksum = None
        log.verbose("Stripped item CHECKSUM is: %s\n" % checksum)
        
        return url, localFile, size, checksum


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
                log.verbose("%s - %s - %s.%s\n" % (filename, errno, errormsg, LINE_OVERWRITE_MID))
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
            

def fetcher( args ):
        
        # get opts
        Str_GetArg = args.get
        Int_SocketTimeout = args.socket_timeout
        Str_DownloadDir = args.download_dir
        Str_CacheDir = args.cache_dir
        Bool_DisableMD5Check = args.disable_md5check
        Int_NumOfThreads = args.num_of_threads
        Str_BundleFile = args.bundle_file
        Str_ProxyHost = args.proxy_host
        Str_ProxyPort = args.proxy_port
        Str_HttpsCertFile = args.https_cert_file
        Str_HttpsKeyFile = args.https_key_file
        Bool_DisableCertCheck = args.disable_cert_check
        Bool_BugReports = args.deb_bugs
        global guiTerminateSignal
        
        if Int_SocketTimeout:
                try:
                        Int_SocketTimeout.__int__()
                        socket.setdefaulttimeout( Int_SocketTimeout )
                        log.verbose( "Default timeout now is: %d.\n" % ( socket.getdefaulttimeout() ) )
                except AttributeError:
                        log.err( "Incorrect value set for socket timeout.\n" )
                        sys.exit( 1 )

        if Str_ProxyHost:
                if Str_ProxyPort:
                        log.verbose(Str_ProxyHost + ":" + str(Str_ProxyPort))
                        proxy_support = urllib2.ProxyHandler({'http': Str_ProxyHost + ":" + str(Str_ProxyPort) })
                        opener = urllib2.build_opener(proxy_support)
                        urllib2.install_opener(opener)
                        log.verbose("Proxy successfully set up with Host %s and port %d\n" % (Str_ProxyHost, Str_ProxyPort))
                else:
                        proxy_support = urllib2.ProxyHandler({'http': Str_ProxyHost})
                        opener = urllib2.build_opener(proxy_support)
                        urllib2.install_opener(opener)
                        log.verbose("Proxy successfully set up with Host %s and default port\n" % (Str_ProxyHost) )

        if (Str_HttpsCertFile and Str_HttpsKeyFile) or Bool_DisableCertCheck:
                context = ssl.create_default_context()

                if Bool_DisableCertCheck:
                        log.verbose("certificate checks for servers are ignored")
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE

                if Str_HttpsCertFile and Str_HttpsKeyFile:
                        log.verbose("cert-file:" + Str_HttpsCertFile + " key-file:" + Str_HttpsKeyFile)
                        context.load_cert_chain(Str_HttpsCertFile, Str_HttpsKeyFile)

                opener = urllib2.build_opener(urllib2.HTTPSHandler(context=context))
                urllib2.install_opener(opener)
                log.verbose("SSL Client Authentication successfully set up with certificate file %s and key file %s\n" % (Str_HttpsCertFile, Str_HttpsKeyFile))
        
        #INFO: Python 2.5 has hashlib which supports sha256
        # If we don't have Python 2.5, disable MD5/SHA256 checksum
        if AptOfflineLib.Python_2_5 is False:
                Bool_DisableMD5Check = True
                log.verbose( "\nMD5/SHA256 Checksum is being disabled. You need atleast Python 2.5 to do checksum verification.\n" )
        
        if Str_GetArg:
                if os.path.isfile(Str_GetArg):
                        log.msg( "\nFetching APT Data\n\n" )
                else:
                        log.err( "File %s not present. Check path.\n" % (Str_GetArg) )
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
                        randomjunk = ''.join(chr(random.randint(97,122)) for x in xrange(5)) if guiBool else ''
                        # 5 byte random junk to make mkdir possible multiple times
                        # use-case -> download many sigs of different machines using one instance
                        tempdir = os.path.join(tempdir , "apt-offline-downloads-" + str(pidname) + randomjunk)
                        os.mkdir(tempdir)
                                
                        Str_DownloadDir = os.path.abspath(tempdir)
                else:
                        log.err( "%s is not writable\n" % (tempdir) ) 
                        errfunc ( 1, '', tempdir)
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
                                errfunc( 1, '' , Str_DownloadDir)
                                
        if Str_BundleFile is not None:
                Str_BundleFile = os.path.abspath(Str_BundleFile)
                if os.access(Str_BundleFile, os.F_OK ):
                        log.err( "%s already present.\nRemove it first.\n" % ( Str_BundleFile ) )
                        sys.exit( 1 )
                else:
                        try:
                                open(Str_BundleFile, 'w')
                        except IOError:
                                log.err("Cannot write to file %s\n" % (Str_BundleFile) )
                                sys.exit(1)

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
                        log.err( "Couldn't find debianbts module. Cannot fetch Bug Reports.\n" )
                        Bool_BugReports = False
        
        FetchData = {} #Info: Initialize an empty dictionary.
        
        #INFO: We don't distinguish in between what to fetch
        # We just rely on what a signature file lists us to get
        # It can be just debs or just package updates or both
        if Str_GetArg is not None:
                try:
                        raw_data_list = open( Str_GetArg, 'r' ).readlines()
                except IOError, ( errno, strerror ):
                        log.err( "%s %s\n" % ( errno, strerror ) )
                        errfunc( errno, '', Str_GetArg)
                        
                FetchData['Item'] = []
                for item in raw_data_list:
                        # Interim fix for Debian bug #664654
                        (ItemURL, ItemFile, ItemSize, ItemChecksum) = stripper(item)
                        if ItemURL.endswith("InRelease"):
                                log.verbose("APT uses new InRelease auth mechanism")
                                ExtraItemURL = ItemURL.rstrip(ItemURL.split("/")[-1])
                                GPGItemURL = "'" + ExtraItemURL + "Release.gpg"
                                ReleaseItemURL = "'" + ExtraItemURL + "Release"
                                ExtraItemFile = ItemFile.rstrip(ItemFile.split("_")[-1])
                                GPGItemFile = ExtraItemFile + "Release.gpg"
                                ReleaseItemFile = ExtraItemFile + "Release"
                                
                                FetchData['Item'].append(GPGItemURL + " " + GPGItemFile + " " + str(ItemSize) + " " + ItemChecksum)
                                log.verbose("Printing GPG URL/Files")
                                log.verbose("%s %s" % (GPGItemURL, GPGItemFile) )

                                FetchData['Item'].append(ReleaseItemURL + " " + ReleaseItemFile + " " + str(ItemSize) + " " + ItemChecksum)
                                log.verbose("Printing Release URL/Files")
                                log.verbose("%s %s" % (ReleaseItemURL, ReleaseItemFile) )
                        FetchData['Item'].append( item )
        del raw_data_list
        
        # INFO: Let's get the total number of items. This will get the
        # correct total count in the progress bar.
        total_items = len(FetchData['Item'])
        
        FetcherInstance = FetcherClass( width=30, lock=True, total_items=total_items )
        
        
        #INFO: Thread Support
        if Int_NumOfThreads > 2:
                log.msg("WARNING: If you are on a slow connection, it is good to\n")
                log.msg("WARNING: limit the number of threads to a low number like 2.\n")
                log.msg("WARNING: Else higher number of threads executed could cause\n")
                log.msg("WARNING: network congestion and timeouts.\n\n")
        
        def DataFetcher(request, response, func=find_first_match):
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

                # On many boxes, the cdrom apt repository will be enabled.
                # For now, let's skip the cdrom repository items.
                if item.startswith("\'cdrom"):
                        log.verbose("cdrom apt repository not supported. Skipping\n")
                        log.verbose(item)
                        return True
                
                #INFO: Everything
                (url, pkgFile, download_size, checksum) = stripper(item)
                thread_name = threading.currentThread().getName()
                log.verbose("Thread is %s\n" % (thread_name) )
                
                if url.endswith(".deb"):
                        try:
                                PackageName = pkgFile.split("_")[0]
                        except IndexError:
                                log.err("Not getting a package name here is problematic. Better bail out.\n")
                                sys.exit(1)
                        
                        #INFO: For Package version, we don't want to fail
                        try:
                                PackageVersion = pkgFile.split("_")[1]
                        except IndexError:
                                PackageVersion = "NA"
                                log.verbose("Weird!! Package version not present. Is it really a deb file?\n")
                        
                        
                        #INFO: find_first_match() returns False or a file name with absolute path
                        full_file_path = func(Str_CacheDir, pkgFile)
                        
                        #INFO: If we find the file in the local Str_CacheDir, we'll execute this block.
                        if full_file_path != False:
                                
                                #INFO: When we copy the payload from the local cache, we need to update the progressbar
                                # Hence we are doing it explicitly for local cache found files
                                FetcherInstance.addItem(download_size)
                                
                                # We'll first check for its md5 checksum
                                if Bool_DisableMD5Check is False:
                                        if FetcherInstance.CheckHashDigest(full_file_path, checksum) is True:
                                                log.verbose("Checksum correct for package %s.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                
                                                bug_fetched = False
                                                if Bool_BugReports:
                                                        log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                        if FetchBugReportsDebian.FetchBugsDebian(PackageName) in [1,2]:
                                                                log.success("Fetched bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                                bug_fetched = True
                                                        else:
                                                                log.verbose("Couldn't fetch bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                                
                                                if Str_BundleFile:
                                                        if FetcherInstance.compress_the_file(Str_BundleFile, full_file_path) is True:
                                                                log.success("%s copied from local cache directory %s.%s\n" % (PackageName, Str_CacheDir, LINE_OVERWRITE_MID) )
                                                                FetcherInstance.updateValue(download_size)
                                                        else:
                                                                log.err("Couldn't add %s to archive %s.%s\n" % (pkgFile, Str_BundleFile, LINE_OVERWRITE_MID) )
                                                                sys.exit(1)
                                                #INFO: If no zip option enabled, simply copy the downloaded package file
                                                # along with the downloaded bug reports.
                                                else:
                                                        try:
                                                                shutil.copy(full_file_path, Str_DownloadDir)
                                                                log.success("%s copied from local cache directory %s.%s\n" % (PackageName, Str_CacheDir, LINE_OVERWRITE_MID) )
                                                                FetcherInstance.updateValue(download_size)
                                                        except shutil.Error:
                                                                log.verbose("%s already available in %s. Skipping copy!!!%s\n" % (pkgFile, Str_DownloadDir, LINE_OVERWRITE_MID) )
                                                        
                                                        if bug_fetched is True:
                                                                for x in os.listdir(os.curdir):
                                                                        if (x.startswith(PackageName) and x.endswith(apt_bug_file_format) ):
                                                                                try:
                                                                                        shutil.move(x, Str_DownloadDir)
                                                                                except:
                                                                                        #INFO: This should fix DBTS #584427
                                                                                        log.verbose("Exception thrown. Most likely it is because the cache_dir and download_dir locations are the same.\n")
                                                                                log.verbose("Moved %s file to %s folder.%s\n" % (x, Str_DownloadDir, LINE_OVERWRITE_FULL) )
                                        #INFO: Damn!! The md5chesum didn't match :-(
                                        # The file is corrupted and we need to download a new copy from the internet
                                        else:
                                                log.verbose("%s checksum mismatch. Skipping file.%s\n" % (pkgFile, LINE_OVERWRITE_FULL) )
                                                log.msg("Downloading %s - %s %s\n" % (PackageName, log.calcSize(download_size/1024), LINE_OVERWRITE_MID) )
                                                if FetcherInstance.download_from_web(url, pkgFile, Str_DownloadDir) == True:
                                                        log.success("\r%s done.%s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                                        
                                                        #Add to Str_CacheDir if possible
                                                        if Str_CacheDir and os.access(Str_CacheDir, os.W_OK) == True:
                                                                try:
                                                                        shutil.copy(pkgFile, Str_CacheDir)
                                                                        log.verbose("%s copied to local cache directory %s.%s\n" % (pkgFile, Str_CacheDir, LINE_OVERWRITE_MID) )
                                                                except shutil.Error:
                                                                        log.verbose("Couldn't copy %s to %s.%s\n" % (pkgFile, Str_CacheDir, LINE_OVERWRITE_FULL) )
                                                                except IOError:
                                                                        # If the underneath file system in mounted read-only, we can't write to it irrespective of dir permissions
                                                                        # IOError: [Errno 30] Read-only file system:
                                                                        log.verbose( "Str_CacheDir %s is not writeable. Is it read-only ??\n" % ( Str_CacheDir ) )
                                                        else:
                                                                log.verbose("cache_dir %s is not writeable. Skipping copy to it.\n" % (Str_CacheDir) )
                                                        
                                                        #Fetch bug reports
                                                        if Bool_BugReports:
                                                                log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                                if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                                        log.success( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                                else:
                                                                        log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                        if Str_BundleFile:
                                                                if FetcherInstance.compress_the_file( Str_BundleFile, pkgFile ) != True:
                                                                        log.err( "Couldn't archive %s to file %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        sys.exit( 1 )
                                                                else:
                                                                        log.verbose( "%s added to archive %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        os.unlink( os.path.join( Str_DownloadDir, pkgFile ) )
                                                        
                                                        # Add to progressbar
                                                        FetcherInstance.updateValue(download_size)
                                #INFO: You're and idiot.
                                # You should NOT disable md5checksum for any files
                                else:
                                        bug_fetched = False
                                        if Bool_BugReports:
                                                log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                        log.success( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                        bug_fetched = True
                                                else:
                                                        log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                            
                                        if Str_BundleFile:
                                                if FetcherInstance.compress_the_file( Str_BundleFile, pkgFile ) != True:
                                                        log.err( "Couldn't archive %s to file %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                        sys.exit( 1 )
                                                else:
                                                        log.verbose( "%s added to archive %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                        os.unlink( os.path.join( Str_DownloadDir, pkgFile ) )
                                        else:
                                                # Since zip file option is not enabled let's copy the file to the target folder
                                                try:
                                                        shutil.copy( full_file_path, Str_DownloadDir )
                                                        log.success( "%s copied from local cache directory %s.%s\n" % ( pkgFile, Str_CacheDir, LINE_OVERWRITE_SMALL ) )
                                                except shutil.Error:
                                                        log.verbose( "%s already available in dest_dir. Skipping copy!!!%s\n" % ( pkgFile, LINE_OVERWRITE_SMALL ) )
                            
                                                # And also the bug reports
                                                if bug_fetched is True:
                                                        for x in os.listdir( os.curdir ):
                                                                if ( x.startswith( PackageName ) and x.endswith( apt_bug_file_format ) ):
                                                                        shutil.move( x, Str_DownloadDir )
                                                                        log.verbose( "Moved %s file to %s folder.%s\n" % ( x, Str_DownloadDir, LINE_OVERWRITE_MID ) )
                                        FetcherInstance.updateValue(download_size)
                                FetcherInstance.completed()
                        else:
                                #INFO: This block gets executed if the file is not found in local Str_CacheDir or Str_CacheDir is None
                                # We go ahead and try to download it from the internet
                                log.verbose( "%s not available in local cache %s.%s\n" % ( pkgFile, Str_CacheDir, LINE_OVERWRITE_MID ) )
                                log.msg( "Downloading %s %s - %s %s\n" % ( PackageName, PackageVersion, log.calcSize( download_size / 1024 ), LINE_OVERWRITE_MID ) )
                                if FetcherInstance.download_from_web( url, pkgFile, Str_DownloadDir ) == True:
                                        #INFO: This block gets executed if md5checksum is allowed
                                        if Bool_DisableMD5Check is False:
                                                #INFO: Debian moved to SHA256. So we use that now. Older systems could have md5
                                                log.verbose( "File %s has checksum %s\n" % ( pkgFile, checksum ) )
                                                if FetcherInstance.CheckHashDigest( pkgFile, checksum ) is True:
                                                        if Str_CacheDir and os.access( Str_CacheDir, os.W_OK ) == True:
                                                                try:
                                                                        shutil.copy( pkgFile, Str_CacheDir )
                                                                        log.verbose( "%s copied to local cache directory %s.%s\n" % ( pkgFile, Str_CacheDir, LINE_OVERWRITE_MID ) )
                                                                except shutil.Error:
                                                                        log.verbose( "%s already available in %s. Skipping copy!!!%s\n" % ( pkgFile, Str_CacheDir, LINE_OVERWRITE_MID ) )
                                                                except IOError:
                                                                        # If the underneath file system in mounted read-only, we can't write to it irrespective of dir permissions
                                                                        # IOError: [Errno 30] Read-only file system:
                                                                        log.verbose( "Str_CacheDir %s is not writeable. Is it read-only ??\n" % ( Str_CacheDir ) )
                                                        else:
                                                                log.verbose( "Str_CacheDir %s is not writeable. Skipping copy to it.\n" % ( Str_CacheDir ) )
                                    
                                                        if Bool_BugReports:
                                                                log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                                if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                                        log.success( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                                else:
                                                                        log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                    
                                                        if Str_BundleFile:
                                                                if FetcherInstance.compress_the_file( Str_BundleFile, pkgFile ) != True:
                                                                        log.err( "Couldn't archive %s to file %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        sys.exit( 1 )
                                                                else:
                                                                        log.verbose( "%s added to archive %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                        os.unlink( os.path.join( Str_DownloadDir, pkgFile ) )
                                                        log.success( "\r%s %s done.%s\n" % ( PackageName, PackageVersion, LINE_OVERWRITE_FULL ) )
                                                else:
                                                        #INFO MD5 Checksum is incorrect.
                                                        log.err( "%s Checksum mismatch.\n" % ( PackageName ) )
                                                        errlist.append( PackageName )
                                        else:
                                                if Bool_BugReports:
                                                        log.verbose("Fetching bug reports for package %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) )
                                                        if FetchBugReportsDebian.FetchBugsDebian( PackageName ) in [1, 2]:
                                                                log.success( "Fetched bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                        else:
                                                                log.verbose( "Couldn't fetch bug reports for package %s.%s\n" % ( PackageName, LINE_OVERWRITE_MID ) )
                                                
                                                if Str_BundleFile:
                                                        if FetcherInstance.compress_the_file( Str_BundleFile, pkgFile ) != True:
                                                                log.err( "Couldn't archive %s to file %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                sys.exit( 1 )
                                                        else:
                                                                log.verbose( "%s added to archive %s.%s\n" % ( pkgFile, Str_BundleFile, LINE_OVERWRITE_SMALL ) )
                                                                os.unlink( os.path.join( Str_DownloadDir, pkgFile ) )
                                    
                                                log.success( "\r%s %s done.%s\n" % ( PackageName, PackageVersion, LINE_OVERWRITE_FULL ) )
                                        
                                        # Add to progressbar
                                        FetcherInstance.updateValue(download_size)
                                else:
                                        errlist.append( PackageName )
                                        
                else:
                        
                        def DownloadPackages(url):
                                if FetcherInstance.download_from_web(url, pkgFile, Str_DownloadDir) == True:
                                        log.success("\r%s done.%s\n" % (url, LINE_OVERWRITE_FULL) )
                                        if Str_BundleFile:
                                                if FetcherInstance.compress_the_file(Str_BundleFile, pkgFile) != True:
                                                        log.err("Couldn't archive %s to file %s.%s\n" % (pkgFile, Str_BundleFile, LINE_OVERWRITE_MID) )
                                                        sys.exit(1)
                                                else:
                                                        log.verbose("%s added to archive %s.%s\n" % (pkgFile, Str_BundleFile, LINE_OVERWRITE_FULL) )
                                                        os.unlink(os.path.join(Str_DownloadDir, pkgFile) )
                                        FetcherInstance.updateValue(download_size)
                                        return True
                                else:
                                        return False
                                
                        #INFO: Handle the multiple Packages formats.
                        # See DTBS #583502
                        SupportedFormats = ["bz2", "gz", "xz", "lzma"]

                        #INFO: We are a package update
                        PackageName = url
                        PackageFile = url.split("/")[-1]
                        PackageFormat = PackageFile.split(".")[-1]
                        if PackageFormat in SupportedFormats:
                                SupportedFormats.remove(PackageFormat) #Remove the already tried format
                        
                        log.msg("Downloading %s.%s\n" % (PackageName, LINE_OVERWRITE_MID) ) 
                        if DownloadPackages(url) is False and guiTerminateSignal is False:
                                # dont proceed retry if Ctrl+C in cli
                                log.verbose("%s failed. Retry with the remaining possible formats\n" % (url) )
                                
                                # We could fail with the Packages format of what apt gave us. We can try the rest of the formats that apt or the archive could support
                                reallyFailed = True
                                for Format in SupportedFormats:
                                        NewPackageFile = PackageFile.split(".")[0] + "." + Format
                                        NewUrl = url.strip(url.split("/")[-1]) + NewPackageFile
                                        log.verbose("Retry download %s.%s\n" % (NewUrl, LINE_OVERWRITE_MID) )
                                        if DownloadPackages(NewUrl) is True:
                                                reallyFailed = False
                                                break
                                        else:
                                                log.verbose("Failed with URL %s.%s\n" % (NewUrl, LINE_OVERWRITE_MID) )
                                if reallyFailed is True:
                                        errlist.append(NewUrl)

        # Create two Queues for the requests and responses
        requestQueue = Queue.Queue()
        responseQueue = Queue.Queue()

        # create size metadata for progress
        for key in FetchData.keys():
                for item in FetchData.get(key):
                        if guiBool:
                                #REAL_PROGRESS: to calculate the total download size, NOTE: initially this was under the loop that Queued the items
                                if guiTerminateSignal:
                                        break
                                try:
                                        (url, pkgFile, download_size, checksum) = stripper(item)
                                        size = int(download_size)
                                        if size == 0:
                                                log.msg("MSG_START")
                                                temp = urllib2.urlopen(url)
                                                headers = temp.info()
                                                size = int(headers['Content-Length'])
                                        totalSize[0] += size
                                except:
                                        log.err("some int parsing problem\n")

            
        if not guiTerminateSignal:
                ConnectThread = AptOfflineLib.MyThread(DataFetcher, requestQueue, responseQueue, Int_NumOfThreads)
            
        ConnectThread.startThreads()
        # Queue up the requests.
        #for item in raw_data_list: requestQueue.put(item)
        for key in FetchData.keys():
                for item in FetchData.get(key):
                        ConnectThread.populateQueue( (key, item) )
        if guiBool:
                log.msg("MSG_END")
                guiMetaCompleted=True
                # For the sake of a responsive GUI
                while (ConnectThread.threads_finished < ConnectThread.threads):
                        # handle signals from gui here
                        if guiTerminateSignal:
                                # stop all ongoing work
                                #TODO: find a way to stop those threads here
                                ConnectThread.guiTerminateSignal=True
                                for thread in ConnectThread.thread_pool:
                                        thread.guiTerminateSignal=True
                                ConnectThread.stopThreads()
                                ConnectThread.stopQueue(timeout=0.2)
                                return
                        ConnectThread.stopThreads()
                        ConnectThread.stopQueue(timeout=0.2)    # let them work for 0.2s
                        log.msg ("[%d/%d]" %(totalSize[1], totalSize[0]))
        else:
                # else go by the normal CLI way
                while ConnectThread.threads_finished < ConnectThread.threads:
                        try:
                                ConnectThread.stopThreads()
                                ConnectThread.stopQueue(0.2)
                        except KeyboardInterrupt:
                                # user pressed Ctrl-c, signal all threads to exit
                                guiTerminateSignal=True # this would signal download_from_web to stop
                                ConnectThread.guiTerminateSignal=True
                                for thread in ConnectThread.thread_pool:
                                        thread.guiTerminateSignal=True      # tell all threads to exit
                                ConnectThread.stopThreads()
                                ConnectThread.stopQueue()
                                log.err("\nInterrupted by user. Exiting!\n")
                                sys.exit(0)
            
        # Print the failed files
        if len(errlist) > 0:
                log.msg("\n\n")
                log.err("The following files failed to be downloaded.\n")
                log.err("Not all errors are fatal. For eg. Translation files are not present on all mirrors.\n")
                for error in errlist:
                        log.err("%s failed.\n" % (error))
        if args.bundle_file:
                log.msg("\nDownloaded data to %s\n" % (Str_BundleFile) )
        else:
                log.msg("\nDownloaded data to %s\n" % (Str_DownloadDir) )
        


def installer( args ):
        
                        
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
                        randomjunk = ''.join(chr(random.randint(97,122)) for x in xrange(5)) if guiBool else ''
                        # 5 byte random junk to make mkdir possible multiple times
                        # use-case -> installing multiple bundles with one dialog
                        tempdir = os.path.join(tempdir , "apt-offline-src-downloads-" + str(pidname) + randomjunk )
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
        
        # Prepare for APT Datbase's Locks
        if Bool_TestWindows:
                log.verbose("In simulate mode. No locking required\n")
        elif FCNTL_LOCK is False:
                log.err("Locking framework in not available on your platform")
                sys.exit(1)
        else:
                AptLock = LockAPT(apt_lists_lock, apt_packages_lock)
                if AptLock is False:
                        log.err("Couldn't acquire lock on the APT Database\n")
                        log.err("Is another process using it\n")
                        sys.exit(1)

                
        try:
                if Bool_TestWindows:
                        log.verbose("In simulate mode. No locking required\n")
                # Acquire APT lock
                elif AptLock.lockLists() is False:
                        log.err("Couldn't acquire lock on %s\nIs another apt process running?\n" % (apt_update_target_path))
                        sys.exit(1)
                
                #INFO: Let's clean the partial database
                for x in os.listdir(apt_update_target_path):
                        x = os.path.join(apt_update_target_path, x)
                        if os.access(x, os.W_OK):
                                os.unlink(x)
                                log.verbose("Cleaning old update data file %s.\n" % (x) )
        except OSError:
                log.err("Cannot find APT's partial cache dir %s\n" % (apt_update_target_path) )
                sys.exit(1)
        finally:
                if Bool_TestWindows:
                        log.verbose("In simulate mode. No locking required\n")
                else:
                        AptLock.unlockLists()
        
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
                sortedKeyList = dictList.keys()
                sortedKeyList.sort()
                for each_bug in sortedKeyList:
                        #INFO: '{}' is the bug split identifier - Used at another place also
                        pkg_name = each_bug.split( '{}' )[-3].split('/')[-1]
                        bug_num = each_bug.split( '{}' )[-2]
                        bug_subject = dictList[each_bug]
                        log.msg( "%s\t%s\t%s\n" % ( bug_num, pkg_name, bug_subject ) )
            
        def magic_check_and_uncompress( archive_file=None, filename=None):
                
                if MagicLib is False:
                        log.err("Please ensure libmagic is installed\n")
                        return False

                magicMIME = AptOfflineMagicLib.open(AptOfflineMagicLib.MAGIC_MIME_TYPE)
                magicMIME.load()
                
                retval = False
                if magicMIME.file( archive_file ) == "application/x-bzip2" or magicMIME.file( archive_file ) == "application/gzip" or magicMIME.file(archive_file) == "application/x-xz":
                        temp_filename = os.path.join(apt_update_target_path, filename + app_name)
                        filename = os.path.join(apt_update_target_path, filename)
                        if magicMIME.file( archive_file ) == "application/x-bzip2":
                                retval = archive.decompress_the_file( archive_file, temp_filename, "bzip2" )
                        elif magicMIME.file( archive_file ) == "application/gzip":
                                retval = archive.decompress_the_file( archive_file, temp_filename, "gzip" )
                        elif magicMIME.file(archive_file) == "application/x-xz":
                                retval = archive.decompress_the_file(archive_file, temp_filename, "xz")
                        else:
                                log.verbose("No filetype match for %s\n" % (filename) )
                                retval = False

                        if retval is True:
                                os.rename(temp_filename, filename)
                        else:
                                try:
                                    os.unlink(temp_filename)
                                except OSError:
                                    log.err("Failed to unlink %s\n" % (temp_filename) )

                elif magicMIME.file( archive_file ) == "application/x-gnupg-keyring" or magicMIME.file( archive_file ) == "application/pgp-signature":
                        gpgFile = os.path.join(apt_update_target_path, filename)
                        shutil.copy2(archive_file, gpgFile)
                        # PGP armored data should be bypassed
                        log.verbose("File is %s, hence 'True'.\n" % (filename) )
                        retval = True
                elif magicMIME.file( archive_file ) == "application/vnd.debian.binary-package" or \
                        magicMIME.file(archive_file) == "application/x-debian-package":
                        debFile = os.path.join(apt_package_target_path, filename)
                        if os.access( apt_package_target_path, os.W_OK ):
                                shutil.copy2( archive_file, debFile )
                                log.msg("%s file synced.\n" % (filename) )
                                retval = True
                        else:
                                log.err( "Cannot write to target path %s\n" % ( apt_package_target_path ) )
                                sys.exit( 1 )
                elif filename.endswith( apt_bug_file_format ):
                        pass
                elif magicMIME.file( archive_file ) == "text/plain":
                        txtFile = os.path.join(apt_update_target_path, filename)
                        if os.access( apt_update_target_path, os.W_OK ):
                                shutil.copy( archive_file, txtFile )
                                retval = True
                        else:
                                log.err( "Cannot write to target path %s\n" % ( apt_update_target_path ) )
                                sys.exit( 1 )
                else:
                        log.err( "I couldn't understand file type %s.\n" % ( filename ) )
                
                if retval:
                        #CHANGE: track progress
                        totalSize[0]+=1 
                        if guiBool:
                                log.msg("[%d/%d]" % (totalSize[0], totalSize[1]))
                        #ENDCHANGE
                        log.verbose( "%s file synced to %s.\n" % ( filename, apt_update_target_path ) )

        def displayBugs(dataType=None):
                ''' Takes keywords "file" or "dir" as type input '''
            
                if dataType is None:
                        return False
                
                # Display the list of bugs
                list_bugs(bugs_number)
                display_options()
                response = get_response()
                
                while True:
                        if response == "?":
                                display_options()
                                response = get_response()
                        elif response.startswith( 'y' ) or response.startswith( 'Y' ):
                                if dataType is "file":
                                        for filename in zipBugFile.namelist():
                                                
                                                #INFO: Take care of Src Pkgs
                                                found = False
                                                for item in SrcPkgDict.keys():
                                                        if filename in SrcPkgDict[item]:
                                                                found = True
                                                                break
                                                        
                                                data = tempfile.NamedTemporaryFile()
                                                data.file.write( zipBugFile.read( filename ) )
                                                data.file.flush()
                                                archive_file = data.name
                                                
                                                if found is True: # found is True. That means this is a src package
                                                        shutil.copy2(archive_file, os.path.join(Str_InstallSrcPath, filename) )
                                                        log.msg("Installing src package file %s to %s.\n" % (filename, Str_InstallSrcPath) )
                                                        continue
                                                
                                                    
                                                if Bool_TestWindows:
                                                        log.verbose("In simulate mode. No locking required\n")
                                                elif AptLock.lockPackages() is False:
                                                        log.err("Couldn't acquire lock on %s\nIs another apt process running?\n" % (archive_file))
                                                        sys.exit(1)
                                                        
                                                magic_check_and_uncompress( archive_file, filename )
        
                                                if Bool_TestWindows:
                                                        log.verbose("In simulate mode. No locking required\n")
                                                else:
                                                        AptLock.unlockLists()
                                                data.file.close()
                                        sys.exit( 0 )
                                if dataType is "dir":
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
                                        full_bug_number = full_bug_file_name.split("{}")[1]
                                        if response == full_bug_number:
                                                bug_file_to_display = full_bug_file_name
                                                found = True
                                                break
                                if found == False:
                                        log.err( "Incorrect bug number %s provided.\n" % ( response ) )
                                        response = get_response()
                                if found:
                                        if dataType is "file":
                                                pydoc.pager(zipBugFile.read(bug_file_to_display) )
                                                # Redisplay the menu
                                                # FIXME: See a pythonic possibility of cleaning the screen at this stage
                                                response = get_response()
                                        if dataType is "dir":
                                                tempFile = open(bug_file_to_display, 'r')
                                                pydoc.pager(tempFile.read() )
                                                # Redisplay the menu
                                                # FIXME: See a pythonic possibility of cleaning the screen at this stage
                                                response = get_response()
                        elif response.startswith( 'r' ) or response.startswith( 'R' ):
                                list_bugs(bugs_number)
                                response = get_response()
                        else:
                                log.err( 'Incorrect choice. Exiting\n' )
                                sys.exit( 1 )

        if os.path.isfile(install_file_path):
                #INFO: For now, we support zip bundles only
                try:
                        zipBugFile = zipfile.ZipFile( install_file_path, "r" )
                except zipfile.BadZipfile:
                        log.err("File %s is not a valid zip file\n" % (install_file_path))
                        sys.exit(1)
                #CHANGE: for progress tracking
                totalSize[1] = len(zipBugFile.namelist())
                totalSize[0] = 0
                #ENDCHANGE
                
                #INFO: Handle source packages with care.
                # Build a dict and populate its files based on details in .dsc
                SrcPkgDict = {}
                
                #TODO: Refactor this loop
                for filename in zipBugFile.namelist():
                        if filename.endswith(".dsc"):
                                SrcPkgName = filename.split('_')[0]
                                temp = tempfile.NamedTemporaryFile()
                                temp.file.write( zipBugFile.read( filename ) )
                                temp.file.flush()
                                temp.file.seek( 0 ) #Let's go back to the start of the file
                                SrcPkgDict[SrcPkgName] = []
                                marker = None
                                for SrcPkgIdentifier in temp.file.readlines():
                                        if SrcPkgIdentifier.startswith('Files:'):
                                                marker = True
                                                continue
                                        
                                        if SrcPkgIdentifier.startswith('\n'):
                                                marker = False
                                                continue
                                        
                                        if marker is True:
                                                SrcPkgData = SrcPkgIdentifier.split(' ')[3].rstrip("\n")
                                                if SrcPkgData in SrcPkgDict[SrcPkgName]:
                                                        break
                                                else:
                                                        SrcPkgDict[SrcPkgName].append(SrcPkgData)
                                        
                                SrcPkgDict[SrcPkgName].append(filename)
                                temp.file.close()
                                
                #if bug_parse_required is True:
                bugs_number = {}
                if Bool_SkipBugReports:
                        log.verbose("Skipping bug report check as requested")
                else:
                        for filename in zipBugFile.namelist():
                                if filename.endswith( apt_bug_file_format ):
                                        temp = tempfile.NamedTemporaryFile()
                                        temp.file.write( zipBugFile.read( filename ) )
                                        temp.file.flush()
                                        temp.file.seek( 0 ) #Let's go back to the start of the file
                                        for bug_subject_identifier in temp.file.readlines():
                                                if bug_subject_identifier.decode('utf8').startswith( 'Subject:' ):
                                                        subject = bug_subject_identifier.lstrip( bug_subject_identifier.split( ":" )[0] )
                                                        subject = subject.rstrip( "\n" )
                                                        break
                                        bugs_number[filename] = subject
                                        temp.file.close()
                                        
                log.verbose(str(bugs_number) + "\n")
                if bugs_number:
                        displayBugs(dataType="file")
                else:
                        log.verbose( "Great!!! No bugs found for all the packages that were downloaded.\n\n" )
                        #response = raw_input( "Continue with Installation. Y/N ?" )
                        #response = response.rstrip( "\r" )
                        #if response.endswith( 'y' ) or response.endswith( 'Y' ):
                        #        log.verbose( "Continuing with syncing the files.\n" )
                        for filename in zipBugFile.namelist():
                                
                                #INFO: Take care of Src Pkgs
                                found = False
                                for item in SrcPkgDict.keys():
                                        if filename in SrcPkgDict[item]:
                                                found = True
                                                break
                                        
                                data = tempfile.NamedTemporaryFile()
                                data.file.write( zipBugFile.read( filename ) )
                                data.file.flush()
                                archive_file = data.name
                                
                                if found is True: #We are src packages. And don't need a lock on the APT Database
                                        shutil.copy2(archive_file, os.path.join(Str_InstallSrcPath, filename) )
                                        log.msg("Installing src package file %s to %s.\n" % (filename, Str_InstallSrcPath) )
                                        continue

                                if Bool_TestWindows:
                                        log.verbose("In simulate mode. No locking required.\n")
                                elif AptLock.lockPackages() is False:
                                        log.err("Couldn't acquire lock on APT\nIs another apt process running?\n")
                                        sys.exit(1)
                                
                                magic_check_and_uncompress( archive_file, filename )

                                if Bool_TestWindows:
                                        log.verbose("In simulate mode. No locking required\n")
                                else:
                                        AptLock.unlockPackages()
                                data.file.close()
                                
        elif os.path.isdir(install_file_path):
                
                SrcPkgDict = {}
                
                #TODO: Needs refactoring with the previous common code
                for filename in os.listdir( install_file_path ):
                        if filename.endswith(".dsc"):
                                SrcPkgName = filename.split('_')[0]
                                SrcPkgDict[SrcPkgName] = []
                                Tempfile = os.path.join(install_file_path, filename)
                                temp = open(Tempfile, 'r')
                                marker = None
                                for SrcPkgIdentifier in temp.readlines():
                                        if SrcPkgIdentifier.startswith('Files:'):
                                                marker = True
                                                continue
                                        
                                        if SrcPkgIdentifier.startswith('\n'):
                                                marker = False
                                                continue
                                        
                                        if marker is True:
                                                SrcPkgData = SrcPkgIdentifier.split(' ')[3].rstrip("\n")
                                                if SrcPkgData in SrcPkgDict[SrcPkgName]:
                                                        break
                                                else:
                                                        SrcPkgDict[SrcPkgName].append(SrcPkgData)
                                SrcPkgDict[SrcPkgName].append(filename)
                                temp.close()
                
                bugs_number = {}
                
                def DirInstallPackages(InstallDirPath):
                        for eachfile in os.listdir( InstallDirPath ):
                                
                                filename = eachfile
                                FullFileName = os.path.abspath(os.path.join(InstallDirPath, eachfile) )
                        
                                if os.path.isdir(FullFileName):
                                        log.verbose("Skipping!! %s is a directory\n" % (FullFileName))
                                        continue
                                #INFO: Take care of Src Pkgs
                                found = False
                                for item in SrcPkgDict.keys():
                                        if filename in SrcPkgDict[item]:
                                                found = True
                                                break
                                if found is True:
                                        shutil.copy2(FullFileName, Str_InstallSrcPath)
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
                                                if bug_subject_identifier.decode('utf8').startswith( 'Subject:' ):
                                                        subject = bug_subject_identifier.lstrip( bug_subject_identifier.split( ":" )[0] )
                                                        subject = subject.rstrip( "\n" )
                                                        break
                                        bugs_number[filename] = subject
                                        temp.close()
                log.verbose(str(bugs_number) + "\n")
                if bugs_number:
                        displayBugs(dataType="dir")
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
                AptSecure = APTVerifySigs(Simulate=Bool_TestWindows)

                lFileList= os.listdir(apt_update_target_path)
                lFileList.sort()
                lVerifiedWhitelist = []
                for localFile in lFileList:
                        localFile = os.path.join(apt_update_target_path, localFile)
                        if localFile.endswith('.gpg'):
                                log.verbose("%s\n" % (localFile) )
                                localFile = os.path.abspath(localFile)
                                if AptSecure.VerifySig(localFile, localFile.rstrip(".gpg") ):
                                        localFile = localFile.rstrip("Release.gpg")
                                        localFile = localFile[:-1] #Remove the trailing _ underscore
                                        localFile = localFile.split("/")[-1]
                                        lVerifiedWhitelist.append(localFile)
                                        log.verbose("%s is gpg clean\n" % (localFile) )
                                else:
                                        # Bad sig.
                                        log.err("%s bad signature. Not syncing because in strict mode.\n" % (localFile) )
                if lVerifiedWhitelist != []:
                        log.verbose (str(lVerifiedWhitelist) + "\n")
                        for whitelist_item in lVerifiedWhitelist:
                                for final_item in lFileList:
                                        if whitelist_item in final_item:
                                                partialFile = os.path.join(apt_update_target_path, final_item)
                                                shutil.copy2(partialFile, apt_update_final_path)
                                                log.msg("%s synced.\n" % (final_item) )

                        

def setter(args):
        #log.verbose(str(args))
        # commented to keep setter UI sane for time
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
                
                                
        #FIXME: We'll use python-apt library to make it cleaner.
        # For now, we need to set markers using shell variables.
        if os.path.isfile(Str_SetArg):
                try:
                        os.unlink(Str_SetArg)
                except OSError:
                        log.err("Cannot remove file %s.\n" % (Str_SetArg) )
        
        
        #Instantiate Apt based on what we have. For now, fall to apt only
        if PythonApt is True:
                AptInst = AptManip(Str_SetArg, Simulate=Bool_TestWindows, AptType="python-apt")
        else:
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
                                AptInst.Upgrade("upgrade", ReleaseType=Str_SetInstallRelease)
                        elif Str_SetUpgradeType == "dist-upgrade":
                                AptInst.Upgrade("dist-upgrade", ReleaseType=Str_SetInstallRelease)
                        elif Str_SetUpgradeType == "dselect-upgrade":
                                AptInst.Upgrade("dselect-upgrade", ReleaseType=Str_SetInstallRelease)
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
        
        if argparse.__version__ >= 1.1:
                parser = argparse.ArgumentParser( prog=app_name, description="Offline APT Package Manager" + ' - ' + version,
                                          epilog=myCopyright + " - " + terminal_license, parents=[global_options])
                parser.add_argument("-v", "--version", action='version', version=version)
        else:
                # Remain backward compatible with older argparse versions 
                parser = argparse.ArgumentParser( prog=app_name, version=app_name + " - " + version,
                                                  description="Offline APT Package Manager", epilog=myCopyright + " - " + terminal_license, parents=[global_options])
        
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
        
        parser_get.add_argument("--proxy-host", dest="proxy_host",
						help="Proxy Host to use", type=str, default=None)
        
        parser_get.add_argument("--proxy-port", dest="proxy_port",
						help="Proxy port number to use", type=int, default=None)
        
        parser_get.add_argument("--https-cert-file", dest="https_cert_file",
						help="Certificate file for https client authentication", type=str, default=None)
        
        parser_get.add_argument("--https-key-file", dest="https_key_file",
						help="Certificate key for https client authentication", type=str, default=None)

        parser_get.add_argument("--disable-cert-check", dest="disable_cert_check",
                          help="Disable Certificate check on https connections", action="store_true")
        
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
        
        
        args = parser.parse_args()

        try:
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
