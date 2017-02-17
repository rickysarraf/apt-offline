
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
import shutil
import platform
import string
import urllib2
import httplib
import Queue
import threading
import subprocess
import socket
import tempfile
import random   # to generate random directory names for installing multiple bundles in on go
import zipfile
import pydoc
import traceback

from ssl import SSLError, SSLEOFError
import zlib

from apt_offline_core.AptOfflineLib import AptOfflineErrors, AptOfflineLibShutilError

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
PythonApt = False
try:
        import apt
        import apt_pkg
        from apt.debfile import DebPackage
        PythonApt = True
except ImportError:
        PythonApt = False
    
from apt_offline_core import AptOfflineLib

#INFO: Set the default timeout to 30 seconds for the packages that are being downloaded.
socket.setdefaulttimeout(30)

# How many times should we retry on socket timeouts
SOCKET_TIMEOUT_RETRY = 5

'''This is the core module. It does the main job of downloading packages/update packages,\n
figuring out if the packages are in the local cache, handling exceptions and many more stuff'''


app_name = "apt-offline"
version = "1.7.2"
myCopyright = "(C) 2005 - 2016 Ritesh Raj Sarraf"
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

       
class FetchBugReports:
        def __init__( self, apt_bug_file_format, IgnoredBugTypes, ArchiveFile=None, lock=False, DownloadDir=None ):
                self.bugsList = []
                self.IgnoredBugTypes = IgnoredBugTypes
                self.lock = lock
                self.apt_bug = apt_bug_file_format
                self.DownloadDir = DownloadDir
                self.ArchiveFile = ArchiveFile
                
                self.fileMgmt = AptOfflineLib.FileMgmt()
                
        
        def FetchBugsDebian( self, PackageName):
                '''0 => False
                1 => No Bug Reports
                2 => True'''
                
                try:
                        #( num_of_bugs, header, self.bugs_list ) = debianbts.get_bugs( 'package', PackageName )
                        self.bugs_list = debianbts.get_bugs( 'package', PackageName )
                        num_of_bugs = len(self.bugs_list)
                except Exception:
                        log.verbose(traceback.format_exc())
                        log.err("Foreign exception raised in module debianbts\n")
                        log.err("Failed to download bug report for package %s\n" % (PackageName))
                        return 0
                        
                
                if num_of_bugs:
                        atleast_one_bug_report_downloaded = False
                        for eachBug in self.bugs_list:
                                
                                # Fetch bug report..
                                # TODO: Handle exceptions later
                                try:
                                        bugReport = debianbts.get_bug_log(eachBug)
                                except Exception:
                                        #INFO: Some of these exceptions are sporadic. For example, this one was hit because of network timeout
                                        # And we don't want the entire operation to fail because of this
                                        log.warn("Foreign exception raised in module debianbts\n")
                                        log.warn("Failed to download bug report for %s\nWill continue to download others\n" % (eachBug))
                                        log.verbose(traceback.format_exc())
                                        continue
                                
                                # This tells us how many follow-ups for the bug report are present.
                                bugReportLength = bugReport.__len__()
                                writeBugReport = 0
                                self.fileName = os.path.join(tempfile.gettempdir(), PackageName + "{}" + str(eachBug) + "{}" + self.apt_bug)
                                file_handle = open( self.fileName, 'w' )
            
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
                                if self.ArchiveFile:
                                    if self.AddToArchive( self.ArchiveFile, self.fileName ):
                                        log.verbose("%s added to file %s\n" % (self.fileName, self.ArchiveFile))
                                    else:
                                        log.warn("%s failed to be added to file %s\n" % (self.fileName, self.ArchiveFile))
                                elif self.DownloadDir:
                                    try:
                                        if self.fileMgmt.move_file(self.fileName, self.DownloadDir):
                                            log.verbose("%s added to download dir %s\n" % (self.fileName, self.DownloadDir))
                                    except AptOfflineLibShutilError, msg:
                                        log.warn("%s\n" % (msg))
                                
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
                try:
                    if self.compress_the_file(ArchiveFile, fileName):
                        if self.file_possibly_deleted is not True:
                                os.unlink(fileName)
                except AptOfflineErrors, message:
                    log.warn("%s\n" % (message))
                return True
        
class ExecCmd:
        def __init__(self, Simulate=False):
                self.Simulate = Simulate

        def Simulate(self):
                if self.Simulate is True:
                        pass
        
        def ExecSystemCmd(self, cmd, sigFile=None):
                '''
                Execute command 'cmd' with subprocess module
                Write stdout to sigFile, if provided
                '''
                if self.Simulate:
                        return True
                
                if sigFile is None: #subprocess.call does take None as an arg
                        fh = None
                else:
                        try:
                                fh = open(sigFile, 'a')
                        except Exception:
                                log.verbose(traceback.format_exc())
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
        def __init__(self, OutputFile, Simulate=False, AptType="apt-get", AptReinstall=False):
                
                ExecCmd.__init__(self, Simulate)
                self.WriteTo = OutputFile
                self.AptReinstall = AptReinstall
                
                if AptType == "apt":
                        self.apt = "apt"
                elif AptType == "apt-get":
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
                elif self.apt == "apt":
                        self.__AptUpdate()
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
                elif self.apt == "apt":
                        self.__AptUpgrade(UpgradeType, ReleaseType)
                elif self.apt == "aptitude":
                        pass
                elif self.apt == "python-apt":
                        # Upgrade is broken in python-apt
                        # Hence for now, redirect to apt-get
                        self.__PythonAptUpgrade(UpgradeType, ReleaseType)
                else:
                        log.err("Method not supported")
                        sys.exit(1)
        
        def InstallPackages(self, PackageList, ReleaseType):
                log.verbose("APT Install Method is of type: %s\n" % self.apt)
                if self.apt == "apt-get":
                        self.__AptGetInstallPackage(PackageList, ReleaseType)
                elif self.apt == "apt":
                        self.__AptInstallPackage(PackageList, ReleaseType)
                elif self.apt == "python-apt":
                        self.__AptInstallPackage(PackageList, ReleaseType)
                else:
                        log.err("Method not supported")
                        sys.exit(1)
                        
        def InstallSrcPackages(self, SrcPackageList, ReleaseType, BuildDependency):
                log.verbose("APT Install Source Method is of type: %s\n" % self.apt)
                if self.apt == "apt-get":
                        self.__AptGetInstallSrcPackages(SrcPackageList, ReleaseType, BuildDependency)
                elif self.apt == "apt":
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
                                
        def __AptUpdate(self):
                log.msg("\nGenerating database of files that are needed for an update.\n")
                if self.ExecSystemCmd(["/usr/bin/apt", "-qq", "--print-uris", "update"], self.WriteTo) is False:
                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                log.verbose("Calling __FixAptSigs to fix the apt sig problem")
                self.__FixAptSigs()
                                        
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
                    self.writeFH = open(self.WriteTo, 'a')
                except Exception:
                    log.verbose(traceback.format_exc())
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

                    self.writeFH.write("'" + item.desc_uri + "'" + " " + destFile + " " + str(item.filesize) + " " + ":" + "\n")
                    log.verbose("Writing string %s %s %d %s to file %s\n" % (item.desc_uri, destFile, item.filesize, ":", self.WriteTo) )
                self.writeFH.flush()
                self.writeFH.close()
        
        def __PythonAptUpgrade(self, UpgradeType="upgrade", ReleaseType=None):
                
                log.verbose("Open file %s for write\n" % self.WriteTo)
                
                try:
                    self.writeFH = open(self.WriteTo, 'a')
                except Exception:
                    log.verbose(traceback.format_exc())
                    log.err("Failed to open file %s for write. Exiting\n")
                    sys.exit(1)
                
                log.msg("\nGenerating database of files that are needed for an upgrade.\n")
                log.warn("Option --upgrade-type not supported with this backend\n")
                log.verbose("\nUsing python apt interface\n")
                
                cache = apt.Cache()
                cache.open(None)
                if UpgradeType == "dist-upgrade":
                    cache.upgrade(dist_upgrade=True)
                elif UpgradeType == "upgrade":
                    cache.upgrade(dist_upgrade=False)
                else:
                    cache.upgrade()
                
                for pkg in cache.get_changes():
                    log.verbose("Generable data is: %s %s %d %s\n" % (pkg.candidate.uri, pkg.candidate.filename.split('/')[-1], pkg.candidate.size, pkg.candidate.md5))
                    self.writeFH.write("%s %s %d %s\n" % (pkg.candidate.uri, pkg.candidate.filename.split('/')[-1], pkg.candidate.size, pkg.candidate.md5))
                self.writeFH.flush()
                self.writeFH.close()

        def __AptUpgrade(self, UpgradeType="upgrade", ReleaseType=None):
                self.ReleaseType = ReleaseType
                
                if ReleaseType is not None:
                        cmd = ["/usr/bin/apt", "-qqq", "--print-uris", "-t"]
                        cmd.append(self.ReleaseType)
                        cmd.append(UpgradeType)
                else:
                        cmd = ["/usr/bin/apt", "-qqq", "--print-uris"]
                        cmd.append(UpgradeType)

                log.msg("\nGenerating database of file that are needed for operation %s\n" % (UpgradeType) )
                if self.ExecSystemCmd(cmd, self.WriteTo) is False:
                        log.err("FATAL: Something is wrong with the APT system\n")

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
                        cmd = ["/usr/bin/apt", "-qqq", "--print-uris", "install", "-t"]
                        cmd.append(self.ReleaseType)
                else:
                        cmd = ["/usr/bin/apt", "-qqq", "--print-uris", "install"]

                for pkg in PackageList:
                        cmd.append(pkg)

                if self.ExecSystemCmd(cmd, self.WriteTo) is False:
                        log.err( "FATAL: Something is wrong with the apt system.\n" )

        def __AptInstallSrcPackages(self, SrcPackageList=None, ReleaseType=None, BuildDependency=False):
                
                self.ReleaseType = ReleaseType
                
                log.msg( "\nGenerating database of source packages %s.\n" % (SrcPackageList) )
                
                if self.ReleaseType is not None:
                        cmd = ["/usr/bin/apt", "-qqq", "--print-uris", "source", "-t"]
                        cmd.append(self.ReleaseType)
                        cmdBuildDep = ["/usr/bin/apt", "-qqq", "--print-uris", "build-dep", "-t"]
                        cmdBuildDep.append(self.ReleaseType)
                else:
                        cmd = ["/usr/bin/apt", "-qqq", "--print-uris", "source"]
                        cmdBuildDep = ["/usr/bin/apt", "-qqq", "--print-uris", "build-dep"]

                for pkg in SrcPackageList:
                        cmd.append(pkg)
                        cmdBuildDep.append(pkg)
                
                if self.ExecSystemCmd(cmd, self.WriteTo) is False:
                        log.err( "FATAL: Something is wrong with the apt system.\n" )
                if BuildDependency:
                        log.msg("Generating Build-Dependency for source packages %s.\n" % (SrcPackageList) )
                        if self.ExecSystemCmd(cmdBuildDep, self.WriteTo) is False:
                                log.err( "FATAL: Something is wrong with the apt system.\n" )
        
                        
        def __AptGetInstallPackage(self, PackageList=None, ReleaseType=None):

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

        def __AptGetInstallSrcPackages(self, SrcPackageList=None, ReleaseType=None, BuildDependency=False):
                
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
                '''
                Initalize keyring based on environment
                Uses python-apt or apt-config
                '''
                
                ExecCmd.__init__(self, Simulate)
                self.defaultPaths = []
                
                if PythonApt is True:
                        apt_pkg.init()
                        self.defaultPaths.append(apt_pkg.config.find_dir('Dir::Etc::trustedparts'))
                        self.defaultPaths.append(apt_pkg.config.find_file('Dir::Etc::trusted'))
                else:
                        command = """
                        # Unset variables in case they are set already
                        unset trusted
                        unset trustedparts
                        # Get the variables from apt
                        eval $(apt-config shell trusted Dir::Etc::trusted/f)
                        eval $(apt-config shell trustedparts Dir::Etc::trustedparts/d)
                        # Securely pass the variables back to python-apt
                        printf "%s\\0%s" "$trusted" "$trustedparts"
                        """
                        process = subprocess.Popen(['sh'], stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE)
                        output = process.communicate(input=command)[0]
                        trusted, trustedparts = output.split('\x00')
                        
                        self.defaultPaths.append(trusted)
                        self.defaultPaths.append(trustedparts)
                log.verbose("APT Signature verification path is: %s\n" % self.defaultPaths)

                if gpgv is None:
                        self.gpgv="/usr/bin/gpgv"
                else:
                        self.gpgv=gpgv
                
                self.opts = []        
                if keyring is None:
                        
                        self.opts.append("--ignore-time-conflict")
                        for eachPath in self.defaultPaths:
                                if os.path.isfile(eachPath):
                                        eachKeyring = "--keyring %s" % (eachPath)
                                        self.opts.extend(eachKeyring.split())
                                elif os.path.isdir(eachPath):
                                        for eachGPG in os.listdir(eachPath):
                                                eachGPG = os.path.join(eachPath, eachGPG)
                                                log.verbose("Adding %s to the apt-offline keyring\n" % (eachGPG) )
                                                eachKeyring = "--keyring %s" % (eachGPG)
                                                self.opts.extend(eachKeyring.split())
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
                except Exception:
                        log.verbose(traceback.format_exc())
                        log.err("Couldn't open lockfile\n")
                        return False
                        
        def lockLists(self):
                try:
                        fcntl.lockf(self.listLock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        return True
                except Exception:
                        log.verbose(traceback.format_exc())
                        return False
                
        def lockPackages(self):
                try:
                        fcntl.lockf(self.pkgLock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        return True
                except Exception:
                        log.verbose(traceback.format_exc())
                        return False
                
        def unlockLists(self):
                try:
                        fcntl.lockf(self.listLock, fcntl.LOCK_UN)
                        return True
                except Exception:
                        log.verbose(traceback.format_exc())
                        return False
        
        def unlockPackages(self):
                try:
                        fcntl.lockf(self.pkgLock, fcntl.LOCK_UN)
                        return True
                except Exception:
                        log.verbose(traceback.format_exc())
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
                                except socket.timeout:
                                        socket_timeout = True
                                        socket_counter += 1
                                except socket.error:
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
    retriable_error_codes = [-3, 13, 504, 404, 403, 401, 10060, 104, 101010]
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
    if errno in retriable_error_codes:
        log.warn("%s - %s - %s %s\n" % (filename, errno, errormsg, LINE_OVERWRITE_FULL))
        log.warn("Will still try with other package uris\n")
    elif errno == 10054:
        log.verbose("%s - %s - %s %s\n" % (filename, errno, errormsg, LINE_OVERWRITE_FULL) )
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
        Str_DownloadDir = args.download_dir
        if not args.basepath is None:
                if not os.path.isabs(args.get):
                        Str_GetArg = os.path.join(args.basepath, os.path.basename(args.get))
                if not os.path.isabs(args.download_dir):
                        Str_DownloadDir = os.path.join(args.basepath, os.path.basename(args.download_dir))
                        if not os.path.exists(Str_DownloadDir):
                                os.mkdir(Str_DownloadDir, 777)

        Int_SocketTimeout = args.socket_timeout
        Str_CacheDir = args.cache_dir
        Bool_DisableMD5Check = args.disable_md5check
        Int_NumOfThreads = args.num_of_threads
        Str_BundleFile = args.bundle_file
        Str_ProxyHost = args.proxy_host
        Str_ProxyPort = args.proxy_port
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
                        
        if Str_CacheDir:
            if os.path.isdir( Str_CacheDir ) is False:
                log.err( "WARNING: cache dir %s is incorrect. Did you give the full path ?\n" % (Str_CacheDir) )
                sys.exit(1)
        
        if not Str_DownloadDir and not Str_BundleFile:
                log.err("Please provide a target download file/folder location.\n")
                sys.exit(1)

        if  Str_DownloadDir:
            if os.path.exists(Str_DownloadDir): 
                if os.path.isdir(Str_DownloadDir):
                    if os.access( Str_DownloadDir, os.W_OK ) is True:
                        Str_DownloadDir = os.path.abspath( Str_DownloadDir )
                    else:
                        log.err("Cannot write to direcotry %s\n" % (Str_DownloadDir))
                        sys.exit(1)
                else:
                    log.err("%s is not a directory\n" % (Str_DownloadDir))
                    sys.exit(1)
            else:
                os.mkdir(Str_DownloadDir)
                #INFO: Because the user may give in a relative path
                Str_DownloadDir = os.path.abspath(Str_DownloadDir)
                log.verbose("Creating directory %s\n" % (Str_DownloadDir))
        else:
            tempdir = tempfile.gettempdir()
            if os.access( tempdir, os.W_OK ):
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

        if Str_BundleFile:
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
        else:
            Str_BundleFile = False

        if Bool_BugReports:
            if DebianBTS is True:
                Bool_BugReports = True
            else:
                log.err( "Couldn't find debianbts module. Cannot fetch Bug Reports.\n" )
                Bool_BugReports = False


        class FetcherClass( DownloadFromWeb, AptOfflineLib.Archiver, AptOfflineLib.Checksum, AptOfflineLib.FileMgmt, FetchBugReports):
                #def __init__( self, width, lock, total_items, BoolCheckSum=False, BoolBundleFile=False, BoolBugReports=False, BoolDownloadDir=False, BoolCacheDir=False):
                def __init__( self, *args, **kwargs):
                        
                        DownloadFromWeb.__init__( self, width=kwargs.pop('width'), total_items=kwargs.pop('total_items') )
                        #ProgressBar.__init__(self, width)
                        #self.width = width
                        AptOfflineLib.Archiver.__init__( self, lock=kwargs.get('lock') )
                        #self.lock = lock
                        AptOfflineLib.FileMgmt.__init__(self)
                        
                        FetchBugReports.__init__(self, apt_bug_file_format, IgnoredBugTypes, Str_BundleFile, lock=kwargs.get('lock'))
                        
                        #INFO: Bunch of important attributes
                        self.CheckSum = Bool_DisableMD5Check
                        self.BundleFile = Str_BundleFile
                        self.BugReports = Bool_BugReports
                        self.DownloadDir = Str_DownloadDir
                        self.CacheDir = Str_CacheDir
                
                
                def verifyPayloadIntegrity(self, payload, checksum):
                    '''Verify the integrity of the payload against the checksum'''
                    
                    if self.CheckSum is True:
                        return True
                    
                    if self.CheckHashDigest(payload, checksum):
                        return True
                    else:
                        return False
                
                def writeData(self, data):
                    '''Write data to backend'''
                    if self.BundleFile is not False:
                        self.writeToArchive(data)
                    else:
                        self.writeToDir(data)
                
                def writeToDir(self, data):
                    '''Write data to directory'''
                    self.copy_file(data, self.DownloadDir)
                
                def writeToArchive(self, data):
                    '''Write data to archive file'''
                    try:
                        self.compress_the_file(self.BundleFile, data)
                    except AptOfflineErrors, message:
                        log.warn("%s\n" % (message))
                
                def writeToCache(self, data):
                    '''Write data to cacheDir'''
                    if self.CacheDir:
                        self.copy_file(data, self.CacheDir)
                
                def processBugReports(self, pkgName):
                    '''Process Bug Reports'''
                    
                    if not self.BugReports:
                        return False
                    
                    log.msg("Fetching bug report for %s%s\n" % (pkgName, LINE_OVERWRITE_FULL))
                    #INFO: Payload is written to destination inside the method
                    self.FetchBugsDebian(pkgName)
                    log.success("Fetched bug report for %s%s\n" % (pkgName, LINE_OVERWRITE_FULL))

                def buildChangelog(self, pkgPath, installedVersion):
                    '''Return latest changes against installedVersion'''
                    constChangelog = "changelog.Debian.gz"
                        
                    if PythonApt is not True:
                        log.err("Cannot provide changelog feature\n")
                        return False
                    else:
                        pkgHandle = DebPackage(pkgPath)
                        for pkgFile in pkgHandle.filelist:
                            if constChangelog in pkgFile:
                                chlogFile = tempfile.NamedTemporaryFile('rw+', bufsize=-1, dir=None, delete=True)
                                pkgLogFile = open(os.path.join(tempfile.gettempdir(), pkgHandle.pkgname + ".changelog"), 'w')

                                #INFO: python-apt is able to read the data from the gzipped changelog dynamically
                                try:
                                    chlogFile.writelines(pkgHandle.data_content(pkgFile).encode('utf-8'))
                                except TypeError:
                                    log.warn("Couldn't extract changelog for package %s\n" % (pkgHandle.pkgname))
                                    log.verbose(traceback.format_exc())
                                    break
                                
                                chlogFile.flush()
                                
                                #Seek to beginning
                                chlogFile.seek(0)
                                
                                for eachLine in chlogFile.readlines():
                                    if installedVersion in eachLine:
                                        break
                                    else:
                                        pkgLogFile.writelines(eachLine)
                                pkgLogFile.flush()
                                if self.ArchiveFile:
                                    if self.AddToArchive(self.ArchiveFile, pkgLogFile.name):
                                        log.verbose("%s added to file %s\n" % (pkgLogFile.name, self.ArchiveFile))
                                    else:
                                        log.warn("%s failed to be added to file %s\n" % (pkgLogFile.name, self.ArchiveFile))
                                else:
                                    try:
                                        if self.move_file(pkgLogFile.name, self.DownloadDir):
                                            log.verbose("%s added to download dir %s\n" % (pkgLogFile.name, self.DownloadDir))
                                    except AptOfflineLibShutilError, msg:
                                        log.warn("%s\n" % (msg))
                                break
        
        FetchData = {} #Info: Initialize an empty dictionary.
        PackageInstalledVersion = {} #INFO: This key/val dict contains record of installed packages
        
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
                        
                        if item.startswith("Changelog/"):
                                (strConstant, pkgName, pkgVersion) = item.split("/")
                                pkgVersion = pkgVersion.strip()
                                PackageInstalledVersion[pkgName] = pkgVersion
                                log.verbose("Added package %s with version %s to dict\n" % (pkgName, pkgVersion))
                        else:
                                # Interim fix for Debian bug #664654
                                (ItemURL, ItemFile, ItemSize, ItemChecksum) = stripper(item)
                                if ItemURL.endswith("InRelease"):
                                        log.verbose("APT uses new InRelease auth mechanism\n")
                                        ExtraItemURL = ItemURL.rstrip(ItemURL.split("/")[-1])
                                        GPGItemURL = "'" + ExtraItemURL + "Release.gpg"
                                        ReleaseItemURL = "'" + ExtraItemURL + "Release"
                                        ExtraItemFile = ItemFile.rstrip(ItemFile.split("_")[-1])
                                        GPGItemFile = ExtraItemFile + "Release.gpg"
                                        ReleaseItemFile = ExtraItemFile + "Release"
                                        
                                        FetchData['Item'].append(GPGItemURL + " " + GPGItemFile + " " + str(ItemSize) + " " + ItemChecksum)
                                        log.verbose("Printing GPG URL/Files\n")
                                        log.verbose("%s %s" % (GPGItemURL, GPGItemFile) )
        
                                        FetchData['Item'].append(ReleaseItemURL + " " + ReleaseItemFile + " " + str(ItemSize) + " " + ItemChecksum)
                                        log.verbose("Printing Release URL/Files\n")
                                        log.verbose("%s %s" % (ReleaseItemURL, ReleaseItemFile) )
                                FetchData['Item'].append( item )
        del raw_data_list
        
        # INFO: Let's get the total number of items. This will get the
        # correct total count in the progress bar.
        total_items = len(FetchData['Item'])
        #BoolCheckSum=False, BoolBundleFile=False, BoolBugReports=False, BoolDownloadDir=False, BoolCacheDir=False):
        FetcherInstance = FetcherClass(Bool_DisableMD5Check, Str_BundleFile, Bool_BugReports, Str_DownloadDir, Str_CacheDir, total_items=total_items, width=30, lock=True)
        
        #INFO: Thread Support
        if Int_NumOfThreads > 2:
                log.msg("WARNING: If you are on a slow connection, it is good to\n")
                log.msg("WARNING: limit the number of threads to a low number like 2.\n")
                log.msg("WARNING: Else higher number of threads executed could cause\n")
                log.msg("WARNING: network congestion and timeouts.\n\n")
        
        def DataFetcher(request, response, func=FetcherInstance.find_first_match):
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
                        if full_file_path is not False:
                            if PackageName in PackageInstalledVersion.keys():
                                    FetcherInstance.buildChangelog(full_file_path, PackageInstalledVersion[PackageName])
                            
                            if FetcherInstance.verifyPayloadIntegrity(full_file_path, checksum):
                                log.success("%s found in cache%s\n" % (PackageName, LINE_OVERWRITE_FULL))
                                #INFO: When we copy the payload from the local cache, we need to update the progressbar
                                # Hence we are doing it explicitly for local cache found files
                                FetcherInstance.addItem(download_size)
                                FetcherInstance.writeData(full_file_path)
                                FetcherInstance.processBugReports(PackageName)
                                FetcherInstance.updateValue(download_size)
                                FetcherInstance.completed()
                            else:
                                log.verbose("%s checksum mismatch. Skipping file %s\n" % (pkgFile, LINE_OVERWRITE_FULL) )
                                log.msg("Downloading %s - %s %s\n" % (PackageName, log.calcSize(download_size/1024), LINE_OVERWRITE_FULL) )
                                if FetcherInstance.download_from_web(url, pkgFile, Str_DownloadDir):
                                    log.success("%s done %s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                    FetcherInstance.writeData(pkgFile)
                                    FetcherInstance.writeToCache(pkgFile)
                                    FetcherInstance.processBugReports(PackageName)
                                    FetcherInstance.updateValue(download_size)
                                else:
                                    errlist.append(PackageName)
                        else:
                            log.msg("Downloading %s - %s %s\n" % (PackageName, log.calcSize(download_size/1024), LINE_OVERWRITE_FULL) )
                            if FetcherInstance.download_from_web(url, pkgFile, Str_DownloadDir):
                                log.success("%s done %s\n" % (PackageName, LINE_OVERWRITE_FULL) )
                                FetcherInstance.writeData(pkgFile)
                                FetcherInstance.writeToCache(pkgFile)
                                FetcherInstance.processBugReports(PackageName)
                                FetcherInstance.updateValue(download_size)
                            else:
                                errlist.append(PackageName)
                else:
                        def DownloadPackages(url):
                            if FetcherInstance.download_from_web(url, pkgFile, Str_DownloadDir):
                                log.success("%s done %s\n" % (url, LINE_OVERWRITE_FULL) )
                                FetcherInstance.writeData(os.path.join(Str_DownloadDir, pkgFile))
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
                        
                        log.msg("Downloading %s %s\n" % (PackageName, LINE_OVERWRITE_FULL) ) 
                        if DownloadPackages(url) is False and guiTerminateSignal is False:
                                # dont proceed retry if Ctrl+C in cli
                                log.verbose("%s failed. Retry with the remaining possible formats\n" % (url) )
                                
                                # We could fail with the Packages format of what apt gave us. We can try the rest of the formats that apt or the archive could support
                                reallyFailed = True
                                for Format in SupportedFormats:
                                        NewPackageFile = PackageFile.split(".")[0] + "." + Format
                                        NewUrl = url.strip(url.split("/")[-1]) + NewPackageFile
                                        log.verbose("Retry download %s %s\n" % (NewUrl, LINE_OVERWRITE_FULL) )
                                        
                                        #INFO: Why are we doing this?
                                        # Because ProgressBar's total_item is fixed
                                        # And download_from_web's addItem() increases the active item upon every
                                        # cycle through apt's backend archive formats
                                        # This ends up resulting in active items being more than total_items
                                        # By increasing the counter, the active/total item list is reflected correctly 
                                        FetcherInstance.items += 1
                                        if DownloadPackages(NewUrl) is True:
                                                reallyFailed = False
                                                break
                                        else:
                                                log.verbose("Failed with URL %s %s\n" % (NewUrl, LINE_OVERWRITE_FULL) )
                                if reallyFailed is True:
                                        errlist.append(NewUrl)
                        FetcherInstance.completed()

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
                                except Exception:
                                        log.verbose(traceback.format_exc())
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
                log.warn("The following files failed to be downloaded.\n")
                log.success("Not all errors are fatal. For eg. Translation files are not present on all mirrors.\n")
                for error in errlist:
                        log.warn("%s failed.\n" % (error))
        if args.bundle_file:
                log.msg("\nDownloaded data to %s\n" % (Str_BundleFile) )
        else:
                log.msg("\nDownloaded data to %s\n" % (Str_DownloadDir) )
        


def installer( args ):
        
    
    class InstallerClass(AptOfflineLib.Archiver, AptOfflineLib.Checksum, AptOfflineLib.FileMgmt, LockAPT):
        def __init__(self, args):
                                      
            # install opts
            self.Str_InstallArg = args.install
            if args.basepath is not None and not os.path.isabs(args.install):
                Str_InstallArg = os.path.join(args.basepath, os.path.basename(args.install))
            self.Bool_TestWindows = args.simulate
            self.Bool_SkipBugReports = args.skip_bug_reports
            self.Bool_Untrusted = args.allow_unauthenticated
            self.Str_InstallSrcPath = args.install_src_path
            self.Bool_SkipChangelog = args.skip_changelog
            self.tempdir = tempfile.gettempdir()
            if not os.access(self.tempdir, os.W_OK):
                log.err("Temporary path %s in not writable. Some functionality may fail\n")
                return False

            AptOfflineLib.Archiver.__init__(self)
            LockAPT.__init__(self, apt_lists_lock, apt_packages_lock)
            
                        
            if self.Str_InstallSrcPath is None:
                pidname = os.getpid()
                randomjunk = ''.join(chr(random.randint(97,122)) for x in xrange(5)) if guiBool else ''
                # 5 byte random junk to make mkdir possible multiple times
                # use-case -> installing multiple bundles with one dialog
                srcDownloadsPath = os.path.join(self.tempdir , "apt-offline-src-downloads-" + str(pidname) + randomjunk )
                os.mkdir(srcDownloadsPath)
                self.Str_InstallSrcPath = os.path.abspath(srcDownloadsPath)
                        
            if not os.path.isdir(self.Str_InstallSrcPath):
                log.err("Not a folder.\n")
                return False
            
            if os.access(self.Str_InstallSrcPath, os.W_OK) is not True:
                log.err("%s is not writable.\n" % (self.Str_InstallSrcPath))
                return False
                
            if self.Bool_TestWindows:
                pidname = os.getpid()
                tempdir = os.path.join(self.tempdir , "apt-package-target-path-" + str(pidname) )
                log.verbose("apt-package-target-path is %s\n" % (tempdir) )
                os.mkdir(tempdir)
                self.apt_package_target_path = os.path.abspath(tempdir)
                    
                tempdir = os.path.join(self.tempdir , "apt-update-target-path-" + str(pidname) )
                log.verbose("apt-update-target-path is %s\n" % (tempdir) )
                os.mkdir(tempdir)
                self.apt_update_target_path = os.path.abspath(tempdir)
                        
                tempdir = os.path.join(self.tempdir , "apt-update-final-path-" + str(pidname) )
                log.verbose("apt-update-final-path is %s\n" % (tempdir) )
                os.mkdir(tempdir)
                self.apt_update_final_path = os.path.abspath(tempdir)
            else:
                self.apt_package_target_path = apt_package_target_path
                self.apt_update_target_path = apt_update_target_path
                self.apt_update_final_path = apt_update_final_path
                
                try:
                    if os.geteuid() != 0:
                        log.err("You need superuser privileges to execute this option\n")
                        return False
                except AttributeError:
                    log.err("Unsupported platform: %s\n" % (platform.platform()))
                    return False
                

        def cleanAptPartial(self, path):
            self.lockLists()
            for eachPath in os.listdir(path):
                eachPath = os.path.abspath(eachPath)
                os.unlink(eachPath)
            self.unlockLists()
            
        def display_options(self,dispType):
            log.msg( "(Y) Yes. Proceed with installation\n" )
            log.msg( "(N) No, Abort.\n" )
            if dispType is "BugReports":
                    log.msg( "(R) Redisplay the list of bugs.\n" )
                    log.msg( "(Bug Number) Display the bug report from the Offline Bug Reports.\n" )
            elif dispType is "Chlog":
                    log.msg( "(C) Display changelog\n")
            log.msg( "(?) Display this help message.\n" )
        
        def get_response(self):
            response = raw_input( "What would you like to do next:\t (y, N, ?)" )
            response = response.rstrip( "\r" )
            return response

        def list_bugs(self, dictList):
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
        
        def magic_check_and_uncompress(self, archive_file=None, filename=None):
                
            if MagicLib is False:
                    log.err("Please ensure libmagic is installed\n")
                    return False

            magicMIME = AptOfflineMagicLib.open(AptOfflineMagicLib.MAGIC_MIME_TYPE)
            magicMIME.load()
            
            retval = False
            if magicMIME.file( archive_file ) == "application/x-bzip2" or magicMIME.file( archive_file ) == "application/gzip" or magicMIME.file(archive_file) == "application/x-xz":
                    temp_filename = os.path.join(self.apt_update_target_path, filename + app_name)
                    filename = os.path.join(self.apt_update_target_path, filename)
                    if magicMIME.file( archive_file ) == "application/x-bzip2":
                        retval = self.decompress_the_file( archive_file, temp_filename, "bzip2" )
                    elif magicMIME.file( archive_file ) == "application/gzip":
                        retval = self.decompress_the_file( archive_file, temp_filename, "gzip" )
                    elif magicMIME.file(archive_file) == "application/x-xz":
                        retval = self.decompress_the_file(archive_file, temp_filename, "xz")
                    else:
                        log.verbose("No filetype match for %s\n" % (filename) )
                        retval = False

                    if retval is True:
                        os.rename(temp_filename, filename)
                    else:
                        log.err("Failed to sync file %s\n" % (filename))
                        try:
                            os.unlink(temp_filename)
                        except OSError:
                            log.warn("Failed to unlink temproary file %s. Check respective decompressor library support\n" % (temp_filename) )

            elif magicMIME.file( archive_file ) == "application/x-gnupg-keyring" or magicMIME.file( archive_file ) == "application/pgp-signature":
                gpgFile = os.path.join(self.apt_update_target_path, filename)
                shutil.copy2(archive_file, gpgFile)
                # PGP armored data should be bypassed
                log.verbose("File is %s, hence 'True'.\n" % (filename) )
                retval = True
            elif magicMIME.file( archive_file ) == "application/vnd.debian.binary-package" or \
                magicMIME.file(archive_file) == "application/x-debian-package":
                debFile = os.path.join(self.apt_package_target_path, filename)
                if os.access( self.apt_package_target_path, os.W_OK ):
                    shutil.copy2( archive_file, debFile )
                    os.chmod(debFile, 0644)
                    log.msg("%s file synced.\n" % (filename) )
                    retval = True
                else:
                    log.err( "Cannot write to target path %s\n" % ( self.apt_package_target_path ) )
                    sys.exit( 1 )
            elif filename.endswith( apt_bug_file_format ):
                pass
            elif magicMIME.file( archive_file ) == "text/plain":
                txtFile = os.path.join(self.apt_update_target_path, filename)
                if os.access( self.apt_update_target_path, os.W_OK ):
                    shutil.copy( archive_file, txtFile )
                    retval = True
                else:
                    log.err( "Cannot write to target path %s\n" % ( self.apt_update_target_path ) )
                    sys.exit( 1 )
            else:
                log.err( "I couldn't understand file type %s.\n" % ( filename ) )
            
            if retval:
                #CHANGE: track progress
                totalSize[0]+=1 
                if guiBool:
                    log.msg("[%d/%d]" % (totalSize[0], totalSize[1]))
                #ENDCHANGE
                log.verbose( "%s file synced to %s.\n" % ( filename, self.apt_update_target_path ) )

        def displayChangelog(self, dataType=None):
            '''Takes file or directory as input'''
            
            chlogFile = tempfile.NamedTemporaryFile()
            chlogPresent = False
            
            if os.path.isdir(dataType):
                for eachItem in os.listdir(dataType):
                    eachItem = os.path.join(dataType, eachItem)
                    if eachItem.endswith(".changelog"):
                        eachFile = open(eachItem, 'r')
                        chlogFile.write(eachFile.read())
                        chlogPresent = True
            elif os.path.isfile(dataType):
                zipLogFile = zipfile.ZipFile(dataType)
                for filename in zipLogFile.namelist():
                    if filename.endswith(".changelog"):
                        chlogFile.write(zipLogFile.read(filename))
                        chlogPresent = True
            else:
                return False
            
            if chlogPresent is False:
                    log.msg("No changelog available\n")
            else:    
                    chlogFile.seek(0)
                    pydoc.pager(chlogFile.read())
            
            self.display_options("Chlog")
            response = self.get_response()
            
            while True:
                if response == "?":
                    self.display_options("Chlog")
                    response = self.get_response()
                elif response.startswith('C') or response.startswith('c'):
                    chlogFile.seek(0)
                    pydoc.pager(chlogFile.read())
                    self.display_options("Chlog")
                    response = self.get_response()
                elif response.startswith('y') or response.startswith('Y'):
                    log.msg("Proceeding with installation\n")
                    break
                else:
                    log.err("Aborting installation, on user request\n")
                    sys.exit(1)
        
        def displayBugs(self, dataType=None):
            ''' Takes keywords "file" or "dir" as type input '''
        
            if dataType is None:
                return False
            
            # Display the list of bugs
            self.list_bugs(bugs_number)
            self.display_options("BugReports")
            response = self.get_response()
            
            while True:
                if response == "?":
                    self.display_options("BugReports")
                    response = self.get_response()
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
                            try:
                                data.file.write( zipBugFile.read( filename ) )
                                data.file.flush()
                            except (zipfile.BadZipfile, zlib.error):
                                log.warn("Failed to read archive file: %s\nContinuing with the rest\n" % (filename))
                                log.verbose(traceback.format_exc())
                                continue
                                #INFO: We can't ranosm the entire payload for a bad CRC for individual files.
                                # The same zip archive, if unarchived with plain unix unizp, works file.
                                # On the internet, there are many bug reports of python's zipfile having certain bugs.
                                # Hence we continue hoping to milk the possible payloads from the archive
                            
                            archive_file = data.name
                            
                            if found is True: # found is True. That means this is a src package
                                shutil.copy2(archive_file, os.path.join(self.Str_InstallSrcPath, filename) )
                                log.msg("Installing src package file %s to %s.\n" % (filename, self.Str_InstallSrcPath) )
                                continue
                            
                                
                            if self.Bool_TestWindows:
                                log.verbose("In simulate mode. No locking required\n")
                            elif self.lockPackages() is False:
                                log.err("Couldn't acquire lock on %s\nIs another apt process running?\n" % (archive_file))
                                sys.exit(1)
                                    
                            self.magic_check_and_uncompress( archive_file, filename )

                            if self.Bool_TestWindows:
                                log.verbose("In simulate mode. No locking required\n")
                            else:
                                self.unlockLists()
                            data.file.close()
                        sys.exit( 0 )
                    if dataType is "dir":
                        if DirInstallPackages(self.Str_InstallArg) is True:
                            sys.exit(0)
                        else:
                            log.err("Failed during install operation on %s.\n" % (self.Str_InstallArg) )
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
                        response = self.get_response()
                    if found:
                        if dataType is "file":
                            pydoc.pager(zipBugFile.read(bug_file_to_display) )
                            # Redisplay the menu
                            # FIXME: See a pythonic possibility of cleaning the screen at this stage
                            response = self.get_response()
                        if dataType is "dir":
                            tempFile = open(bug_file_to_display, 'r')
                            pydoc.pager(tempFile.read() )
                            # Redisplay the menu
                            # FIXME: See a pythonic possibility of cleaning the screen at this stage
                            response = self.get_response()
                elif response.startswith( 'r' ) or response.startswith( 'R' ):
                    self.list_bugs(bugs_number)
                    response = self.get_response()
                else:
                    log.err( 'Incorrect choice. Exiting\n' )
                    sys.exit( 1 )
                  
    InstallerInstance = InstallerClass(args)
    installPath = InstallerInstance.Str_InstallArg
    if os.path.isfile(installPath):
        #INFO: For now, we support zip bundles only
        try:
            zipBugFile = zipfile.ZipFile( installPath, "r" )
        except zipfile.BadZipfile:
            log.err("File %s is not a valid zip file\n" % (installPath))
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

        # Let's display changelog
        if InstallerInstance.Bool_SkipChangelog:
            log.verbose("Skipping display of changelog as requested\n")
        else:
            InstallerInstance.displayChangelog(InstallerInstance.Str_InstallArg)
                                
        #if bug_parse_required is True:
        bugs_number = {}
        if InstallerInstance.Bool_SkipBugReports:
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
            InstallerInstance.displayBugs(dataType="file")
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
                    shutil.copy2(archive_file, os.path.join(InstallerInstance.Str_InstallSrcPath, filename) )
                    log.msg("Installing src package file %s to %s.\n" % (filename, InstallerInstance.Str_InstallSrcPath) )
                    continue

                if InstallerInstance.Bool_TestWindows:
                    log.verbose("In simulate mode. No locking required.\n")
                elif InstallerInstance.lockPackages() is False:
                    log.err("Couldn't acquire lock on APT\nIs another apt process running?\n")
                    sys.exit(1)
                
                InstallerInstance.magic_check_and_uncompress( archive_file, filename )

                if InstallerInstance.Bool_TestWindows:
                    log.verbose("In simulate mode. No locking required\n")
                else:
                    InstallerInstance.unlockPackages()
                data.file.close()
                            
    elif os.path.isdir(installPath):
        SrcPkgDict = {}
        
        #TODO: Needs refactoring with the previous common code
        for filename in os.listdir( installPath ):
            if filename.endswith(".dsc"):
                SrcPkgName = filename.split('_')[0]
                SrcPkgDict[SrcPkgName] = []
                Tempfile = os.path.join(installPath, filename)
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
                                shutil.copy2(FullFileName, InstallerInstance.Str_InstallSrcPath)
                                log.msg("Installing src package file %s to %s.\n" % (filename, InstallerInstance.Str_InstallSrcPath) )
                                continue
                        
                        InstallerInstance.magic_check_and_uncompress( FullFileName, filename )
                return True

        # Let's display changelog
        if InstallerInstance.Bool_SkipChangelog:
            log.verbose("Skipping display of changelog as requested\n")
        else:
            InstallerInstance.displayChangelog(InstallerInstance.Str_InstallArg)
                                
        bugs_number = {}                        
        if InstallerInstance.Bool_SkipBugReports:
                log.verbose("Skipping bug report check as requested")
        else:
                for filename in os.listdir( installPath ):
                        if filename.endswith( apt_bug_file_format ):
                                filename = os.path.join(installPath, filename)
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
                InstallerInstance.displayBugs(dataType="dir")
        else:
                log.verbose( "Great!!! No bugs found for all the packages that were downloaded.\n\n" )
                DirInstallPackages(installPath)
    else:
        log.err("Invalid path argument specified: %s\n" % (installPath))
        sys.exit(1)
                        
    if InstallerInstance.Bool_Untrusted:
            log.err("Disabling apt gpg check can risk your machine to compromise.\n")
            for x in os.listdir(apt_update_target_path):
                    x = os.path.join(apt_update_target_path, x)
                    shutil.copy2(x, apt_update_final_path) # Do we do a move ??
                    log.verbose("%s %s\n" % (x, apt_update_final_path) )
                    log.msg("%s synced.\n" % (x) )
    else:
            AptSecure = APTVerifySigs(Simulate=InstallerInstance.Bool_TestWindows)

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
        if args.basepath is not None and not os.path.isabs(args.set):
                Str_SetArg = os.path.join(args.basepath, os.path.basename(args.set))

        List_SetInstallPackages = args.set_install_packages
        List_SetInstallSrcPackages = args.set_install_src_packages
        Str_SetInstallRelease = args.set_install_release
        Bool_SetUpdate = args.set_update
        Bool_SetUpgrade = args.set_upgrade
        Str_SetUpgradeType = args.upgrade_type
        Bool_SrcBuildDep = args.src_build_dep
        Bool_TestWindows = args.simulate
        Bool_Changelog = args.generate_changelog
        
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
        
        
        # Pick apt backend based on what option the user chose
        AptInst = AptManip(Str_SetArg, Simulate=Bool_TestWindows, AptType=args.apt_backend)
        
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
        
        if Bool_Changelog:
            if not PythonApt:
                #INFO: No crude ways. Will only work with python-apt
                log.err("Cannot provide changelog without proper backend support\n")
                sys.exit(1)

            log.verbose("Initializing apt cache\n")
            aptCache = apt.Cache()
            aptCache.open()
            
            try:
                    sigFile = open(Str_SetArg, 'rw+')
            except Exception:
                    log.err(traceback.format_exc())
            
            for eachLine in sigFile.readlines():
                    (pkgUrl, pkgFile, pkgSize, pkgChecksum) = stripper(eachLine)
                    pkgName = pkgFile.split("_")[0]
                    try:
                            pkgMeta = aptCache[pkgName]
                            pkgInstalledVersion = pkgMeta.installed.version
                    except AttributeError:
                            log.verbose("Package %s is not installed. Thus no changelog\n")
                            continue
                    except KeyError:
                            #INFO: For --update, we'll get an obvious key error because those aren't
                            # packages, but just source URLs.
                            log.verbose("Cannot find package %s in package cache\n" % (pkgName))
                            continue
                    except Exception:
                            log.err(traceback.format_exc())
                            raise
                    
                    #INFO: '/' will be the delimeter
                    log.verbose("Writing to Changelog, pkgName: %s, pkgInstalledVersion %s\n" % (pkgName, pkgInstalledVersion))
                    sigFile.writelines("Changelog/%s/%s\n" % (pkgName, pkgInstalledVersion))


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
        global_options.add_argument("--basepath", dest="basepath", help="Set removeable storage base path")
        
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
        
        parser_set.add_argument('set', nargs='?',
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
        
        parser_set.add_argument("--generate-changelog", dest="generate_changelog",
                                help="Generate changelog of the version to be downloaded", action="store_true")
        
        parser_set.add_argument("--apt-backend", dest="apt_backend", help="APT backend to use. One of: apt, apt-get, python-apt",
                          action="store", type=str, metavar="apt-get", default="apt-get")
        
        # GET command options
        parser_get = subparsers.add_parser('get', parents=[global_options])
        
        #INFO: When get option is called, call the fetcher() function
        parser_get.set_defaults(func=fetcher)
        
        parser_get.add_argument('get', nargs='?',
                          help="Get apt-offline data",
                          action="store", type=str, metavar="apt-offline.sig",
                          default="apt-offline.sig")
        
        parser_get.add_argument("--socket-timeout", dest="socket_timeout", help="Set Socket Timeout",
                        action="store", type=int, metavar="30", default=30)
        
        parser_get.add_argument("-d", "--download-dir", dest="download_dir",
                          help="Folder path to save files to", action="store",
                          type=str, metavar="apt-downloads",
                          default="apt-offline-download")
        
        parser_get.add_argument("-s", "--cache-dir", dest="cache_dir",
                          help="Cache folder to search for",
                          action="store", type=str, metavar="/var/cache/apt/archives/")
        
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
        
        # INSTALL command options
        parser_install = subparsers.add_parser('install', parents=[global_options])
        parser_install.set_defaults(func=installer)
        
        parser_install.add_argument('install', nargs='?',
                          help="Install apt-offline data, a bundle file or a directory",
                          action="store", type=str, metavar="apt-offline-download.zip | apt-offline-download/",
                          default="apt-offline-download")

        parser_install.add_argument("--install-src-path", dest="install_src_path",
                                    help="Install src packages to specified path.", default=None)
        
        parser_install.add_argument("--skip-bug-reports", dest="skip_bug_reports",
                        help="Skip the bug report check", action="store_true")
        
        parser_install.add_argument("--skip-changelog", dest="skip_changelog",
                                    help="Skip display of changelog", action="store_true")
        
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
