#!/usr/bin/env python
# pypt-offline.py
# version devel

############################################################################
#    Copyright (C) Ritesh Raj Sarraf                                       #
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
#    Free Software F[-d] [-s] [-u]oundation, Inc.,                         #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import os, shutil, string, urllib, sys, optparse, urllib2, progress 

def download_from_web(sUrl, sFile, sSourceDir):
    """Download the required file from the web
       The arguments are passed everytime to the function so that,
       may be in future, we could reuse this function"""
    bFound = False
        #errfunc(temp_decode(X))
    print "\n", sFile," not available. Downloading from " + sUrl + "!"
    
    try:
        os.chdir(sSourceDir)
        
        #NOTE: Obsoleting this in favor of implementing a progress bar
        #temp = urllib2.urlopen(sUrl)
        #data = open(sFile,'wb')
        #data.write(temp.read())
        #data.close()
        #temp.close()
        
        urllib.urlretrieve(sUrl, sFile, reporthook=progress.myReportHook)
        bFound = True
        #shutil.move(temp, sFile)
        #(temp, dStatus) = urllib.urlretrieve(url,file,reporthook=report)
        #print "dStatus reports "+ str(dStatus)
    #except IOError, (errno, strerror, fileattr):
        #if hasattr(X, 'Not Found'):
            #print "Got 404\n"
        #errfunc(X)
        #print "Failed\n"
    except OSError, (errno, strerror):
        print sSourceDir
        errfunc(errno, strerror)
        
    except urllib2.HTTPError, errstring:
        #if hasattr(errstring, '404'):
            #print "I got 404 page"
        #print errstring
        errfunc(errstring.code, errstring.msg)
        
    except urllib2.URLError, errstring:
        #print errstring
        errfunc(0, errstring.msg)
        pass
    
    except IOError, (errno, strerror):
        print strerror
        errfunc(errno, strerror)
        
    #os.environ['FILE_DOWNLOAD'] = url
    #os.system('wget $FILE_DOWNLOAD') # In this case you require a valid .wgetrc file
    #print file," downloaded from the net\n"
    return bFound

#TODO: walk_tree_copy_debs
# This might require simplification and optimization.
# But for now it's doing the job.
# Need to find a better algorithm, maybe os.walk()                    
def walk_tree_copy_debs(sRepository, sFile, sSourceDir):
    """This function checks for a package to see if its already downloaded
    It can search directories with depths."""
    #The core algorithm is here for the whole program to function'\n'
    #It recursively searches a tree/subtree of folders for package files'\n'
    #like the directory structure of "apt-proxy". If files are found (.deb || .rpm)'\n'
    #it checks wether they are on the list of packages to be fetched. If yes,'\n\
    #it copies them. Same goes for flat "apt archives folders" also.'\n'
    #Else it fetches the package from the net"""
    bFound = False
    try:
        if sRepository is not None:
            for name in os.listdir(sRepository):
                path = os.path.join(sRepository, name)
                if os.path.isdir(path):
                    walk_tree_copy_debs(path, sFile, sSourceDir)
                elif name.endswith('.deb') or name.endswith('.rpm'):
                    if name == sFile:
                        shutil.copy(path, sSourceDir)
                        bFound = True
                        break    
            return bFound
    except OSError, (errno, strerror):
        print errno, strerror
        errfunc(errno)
        
        
#def errfunc(error_number, error_code, error_string):

def errfunc(errno, errormsg):
    """We use errfunc to handler errors.
    There are some error codes (-3 and 13 as of now)
    which are temporary codes, they happen when there
    is a temporary resolution failure, for example.
    For such situations, we can't abort because the
    uri file might have other hosts also, which might
    be well accessible.
    This function does the job of behaving accordingly
    as per the error codes."""
    
    if errno == -3 or errno == 13:
        #TODO: Find out what these error codes are for
        # and better document them the next time you find it out.
        pass
    elif errno == 407 or errno == 2:
        # These, I believe are from OSError/IOError exception.
        # I'll document it as soon as I confirm it.
        print errormsg
        sys.exit(errno)
    elif errno == 504 or errno == 404:
        #TODO: Counter which will inform that some packages weren't fetched.
        # A counter needs to be implemented which will at the end inform the list of sources which 
        # failed to be downloaded with the above codes.
        
        # 504 is for gateway timeout
        # On gateway timeouts we can keep trying out becuase
        # one apt source.list might have different hosts.
        # 404 is for URL error. Page not found.
        # THere can be instances where one source is changed but the rest are working.
        print errormsg
        print "Will still try with other package uris"
        pass
    else:
        print "Aiee! I didn't understand the errorcode ", errno
        sys.exit(errno)
    
def warn(exception_warn):
    sys.stderr.write(exception_warn)

#FIXME: Exception Handling
# This was one of the worst implementions I had thought of
# I'm happy I got rid of this. :-)
def decode_exceptions(X):
    # I need to find out a better way to implement this.
    if number_of_variables(X) is 2:
        (errcode, errstring) = X
        return errcode, errstring
    elif number_of_variables(X) is 3:
        (errno, temperr) = X
        (errcode, errstring) = temperr
        del temperr
        return errno, errcode, errstring
    else:
        return str(X)

def number_of_variables(X):
    counter = 0
    for variables in X:
        counter += 1
    return counter

def report(blockcount, bytesdownloaded, totalbytes):
    # This isn't implemented yet.
    # When implemented this would give a progress bar.        
    sys.stdout.write("\rDownloading %r from %r ... (%r of %r)" % (blockcount, bytesdownloaded, totalbytes,))
    sys.stdout.write("\rDownloading ... (%r of %r)" % (blockcount, bytesdownloaded,totalbytes,))
    sys.stdout.flush()

#class OptionParser(optparse.OptionParser):
#    
#    def check_required(self, opt1, opt2, opt3):
#        for x in opt1, opt2, opt3:
#            #option = self.get_option(opt)
#            option = self.get_option(x)
#        
#        # Assumes the options's default is set to 'None'
#        if getattr(self.values, option.dest) is None:
#            self.error("%s option not supplied" % x)
# Let's first open the RAW_URIS file and read it all.
def starter(uri, path, cache, type):
    """uri - The uri data whill will contain the information
    path - The path (if any) where the download needs to be done
    cache - The cache (if any) where we should check before downloading from the net
    type - type is basically used to identify wether it's a update download or upgrade download"""
    
    if type == 1: # Oh! We're only downloading the update package list database
        
        if path is None:
            if os.access("pypt-downloads", os.W_OK) is True:
                sSourceDir = os.path.abspath("pypt-downloads")
            else:
                os.mkdir("pypt-downloads")
                sSourceDir = os.path.abspath("pypt-downloads")
        else:
                sSourceDir = path
        
        try:
            lRawData = open(uri, 'r').readlines()
        except IOError, (errno, strerror):
            print errno, strerror
            errfunc(errno)
        
        for each_single_item in lRawData:
            lSplitData = each_single_item.split(' ') # Split on the basis of ' ' i.e. space
    
            # We initialize the variables "sUrl" and "sFile" here.
            # We also strip the single quote character "'" to get the real data
            sUrl = string.rstrip(string.lstrip(''.join(lSplitData[0]), chars="'"), chars="'")
            sFile = string.rstrip(string.lstrip(''.join(lSplitData[1]), chars="'"), chars="'")
            
            #NOTE: We don't check for local cache because checking the sRepository for update packages
            # would be stupidity.
            bStatus = download_from_web(sUrl, sFile, sSourceDir)
            if bStatus == True:
                 print sFile + " successfully downloaded from " + sUrl + "\n."
            else:
                 print sFile + " not downloaded from " + sUrl + ".\n"
    #sSourceDir = path
    if path is None:
        if os.access("pypt-downloads", os.W_OK) is True:
            sSourceDir = "pypt-downloads"
        else:
            os.mkdir("pypt-downloads")
            sSourceDir = "pypt-downloads"
    else:
        sSourceDir = path
            
    if cache is None:
        sRepository = os.curdir
    else:
        sRepository = cache
        
    try:
        lRawData = open(uri, 'r').readlines()
    except IOError, (errno, strerror):
        print errno, strerror
        errfunc(errno)
    
    for each_single_item in lRawData:
        lSplitData = each_single_item.split(' ') # Split on the basis of ' ' i.e. space

        # We initialize the variables "sUrl" and "sFile" here.
        # We also strip the single quote character "'" to get the real data
        sUrl = string.rstrip(string.lstrip(''.join(lSplitData[0]), chars="'"), chars="'")
        sFile = string.rstrip(string.lstrip(''.join(lSplitData[1]), chars="'"), chars="'")
        bStatus = walk_tree_copy_debs(sRepository, sFile, sSourceDir)
        if bStatus == True:
            print sFile + " sccessfully copied from local cache " + sRepository + ".\n"
        else:
            bStatus = download_from_web(sUrl, sFile, sSourceDir)
            if bStatus == True:
                 print sFile + " successfully downloaded from " + sUrl + "\n."
            else:
                 print sFile + " not downloaded from " + sUrl + "and NA in local cache - " + sRepository + ".\n"
           
if __name__ == "__main__":
    
    try:
        version = "0.6b"
        reldate = "03/10/2005"
        copyright = "(C) 2005 Ritesh Raj Sarraf - RESEARCHUT (http://www.researchut.com/)"
    
        #FIXME: Option Parsing
        # There's a flaw with either optparse or I'm not well understood with it
        # Presently you need to provide all the arguments to it to work.
        # No less, no more. This needs to be converted to getopt sometime.
        
        #parser = OptionParser()
        #parser = optparse.OptionParser()
        parser = optparse.OptionParser(usage="%prog [OPTION1, OPTION2, ...]", version="%prog " + version)
        parser.add_option("-d","--download-dir", dest="download_dir", help="Root directory path to save the downloaded files", action="store", type="string", metavar="pypt-downloads")
        #parser.set_defaults(download_dir="pypt-downloads")
        parser.add_option("-s","--cache-dir", dest="cache_dir", help="Root directory path where the pre-downloaded files will be searched. If not, give a period '.'",action="store", type="string", metavar=".")
        #parser.set_defaults(cache_dir=".")
        #parser.set_defaults(cache_dir=".")
        parser.add_option("-u","--uris", dest="uris_file", help="Full path of the uris file which contains the main database of files to be downloaded",action="store", type="string")
        
        #TODO: Add updation
        # The new plan is to make pypt-offline do the updation and upgradation from within its own interface instead of expecting
        # the user to do the dirty part. We'll add options which'll take care of it.
        # For this we'll have additional options
        # --set-update - This will extract the list of uris which need to be fetched for _updation_. This command must be executed on the NONET machine.
        # --fetch-update - This will fetch the list of uris which need for apt's databases _updation_. This command must be executed on the WITHNET machine.
        # --install-update - This will install the fetched database files to the  NONET machine and _update_ the apt database on the NONET machine. This command must be executed on the NONET machine.
        # The same will happen for upgradation.
        # --set-upgrade - This will extract the list of uris which need to be fetched for _upgradation_. This command must be executed on the NONET machine.
        # --fetch-upgrade - This will fetch the list of uris which need for apt's databases _upgradation_. This command must be executed on the WITHNET machine.
        # --install-upgrade - This will install the fetched database files to the  NONET machine and _upgrade_ the packages. This command must be executed on the NONET machine.
        parser.add_option("","--set-update", dest="set_update", help="Extract the list of uris which need to be fetched for _updation_", action="store", type="string", metavar="pypt-offline-update.dat")
        #parser.set_defaults(set_update="pypt-offline-update.dat")
        parser.add_option("","--fetch-update", dest="fetch_update", help="Fetch the list of uris which are needed for apt's databases _updation_. This command must be executed on the WITHNET machine", action="store", type="string", metavar="pypt-offline-update.dat")
        #parser.set_defaults(fetch_update="pypt-offline-update.dat")
        parser.add_option("","--install-update", dest="install_update", help="Install the fetched database files to the  NONET machine and _update_ the apt database on the NONET machine. This command must be executed on the NONET machine", action="store", type="string", metavar="pypt-offline-update-fetched.zip")
        #parser.set_defaults(install_update="pypt-offline-update-fetched.zip")
        parser.add_option("","--set-upgrade", dest="set_upgrade", help="Extract the list of uris which need to be fetched for _upgradation_", action="store", type="string", metavar="pypt-offline-upgrade.dat")
        #parser.set_defaults(set_upgrade="pypt-offline-upgrade.dat")
        parser.add_option("","--upgrade-type", dest="upgrade_type", help="Type of upgrade to do. Use one of upgrade, dist-upgrade, dselect-ugprade", action="store", type="string", metavar="upgrade")
        #parser.set_defaults(upgrade_type="upgrade")
        parser.add_option("","--fetch-upgrade", dest="fetch_upgrade", help="Fetch the list of uris which are needed for apt's databases _upgradation_. This command must be executed on the WITHNET machine", action="store", type="string", metavar="pypt-offline-upgrade.dat")
        #parser.set_defaults(fetch_upgrade="pypt-offline-upgrade.dat")
        parser.add_option("","--install-upgrade", dest="install_upgrade", help="Install the fetched packages to the  NONET machine and _upgrade_ the packages on the NONET machine. This command must be executed on the NONET machine", action="store", type="string", metavar="pypt-offline-update-fetched.zip")
        #parser.set_defaults(install_ugprade="pypt-offline-update-fetched.zip")
        (options, args) = parser.parse_args()
        #parser.check_required("-d", "-s", "-u")
        #if len(arguments) != 2:
        #    parser.error("Err! Incorrect number of arguments. Exiting")
        #print len(args)
        #if len(options) != 1 or len(options) > 2:
        #    print len(args)
        #    parser.error("No arguments were passed\n")
        #    sys.exit(1)
            
        
        #sRawUris = options.uris_file
        #if sRawUris is None:
        #    if os.access("pypt-offline-update.dat", os.R_OK) is True:
        #        sRawUris = "pypt-offline-update.dat"
        
            
        print "pypt-offline %s" % version
        print "Copyright %s" % copyright
        #print """\n\nThis program is still in it's very early stage. There can be situations
        #where things might not work as expected. Please direct all errors, bugs,suggestions
        #etc to me at rrs@researchut.com\n\n\n"""
        
        print type(options.set_update)
        if options.set_update:
            if os.getuid() != 0:
                parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
            #options.set_update = "pypt-offline-update.dat"
            #FIXME: More platforms need to be added -- FIXED
            # We're using linux2, gnu0 and gnukfreebsd5 as the only platforms because these are the only platforms
            # upon which apt has been ported under Debian.
            if sys.platform == "linux2" or sys.platform == "gnu0" or sys.platform == "gnukfreebsd5":
                print "Generating database of files that are needed for an update.\n"
                os.chdir(options.set_update)
                os.system('/usr/bin/apt-get -qq --print-uris update > pypt-offline-update.dat')
            else:
                parser.error("This argument is supported only on Unix like systems with apt installed\n")
                #TODO: Implement --set-update using _maybe_ apt
            sys.exit(0)

        if options.set_upgrade or options.upgrade_type:
            if not (options.set_upgrade and options.upgrade_type):
                parser.error("Options --set-upgrade and --upgrade-type are mutually inclusive\n")
            else:
                if os.getuid() != 0:
                    parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                
                if sys.platform == "linux2" or sys.platform == "gnu0" or sys.platform == "gnukfreebsd5":
                    os.chdir(options.set_upgrade)
                    if options.upgrade_type == "upgrade":
                        print "Generating database of files that are needed for an upgrade.\n"
                        os.system('/usr/bin/apt-get -qq --print-uris upgrade > pypt-offline-upgrade.data')
                    elif options.upgrade_type == "dist-upgrade":
                        print "Generating database of files that are needed for an upgrade.\n"
                        os.system('/usr/bin/apt-get -qq --print-uris dist-upgrade > pypt-offline-upgrade.data')
                    elif options.upgrade_type == "dselect-upgrade":
                        print "Generating database of files that are needed for an upgrade.\n"
                        os.system('/usr/bin/apt-get -qq --print-uris dselect-upgrade > pypt-offline-upgrade.data')
                    else:
                        parser.error("Invalid upgrade argument type selected\nPlease use one of, upgrade/dist-upgrade/dselect-upgrade\n")
                else:
                    parser.error("This argument is supported only on Unix like systems with apt installed\n")
                sys.exit(0)
            
        if options.fetch_update:
            #TODO: Updation
            # Implement below similar code for updation
            print "Fetching uris which update apt's package database\n"
            
            # This function will take two arguments. uris file and download type
            # If the uris file is an update database it shouldn't do filetype (.deb/.rpm)
            # checking.
            # Since we're in fetch_update, the download_type will be non-deb/rpm data
            #foo(sRawUris, download_type)
            # 1 is for update packages 
            # 2 is for upgrade packages
            download_type = 1
            starter(options.fetch_update, options.download_dir, options.cache_dir, download_type)
            
            #if sRawUris is None:
            #    if os.access("pypt-offline-update.dat", os.R_OK) is True:
            #        sRawUris = "pypt-offline-update.dat"
            
    
    except KeyboardInterrupt:
        print "\nReceived immediate EXIT signal. Exiting!\n"