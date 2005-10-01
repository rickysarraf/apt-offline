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
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import os, shutil, string, urllib, sys, optparse, urllib2

def download_from_web(sUrl, sFile, sSourceDir):
    """Download the required file from the web
       The arguments are passed everytime to the function so that,
       may be in future, we could reuse this function"""
    bFound = False
    try:
        os.chdir(sSourceDir)
    except IOError, (errno, strerror):
        #decode_exceptions(X)
        print errno, strerror
        errfunc(errno)
        #errfunc(decode_exceptions(X))
    except OSError, (errno, strerror):
        print errno, strerror
        errfunc(errno)
        #errfunc(temp_decode(X))
    print "\n", sFile," not available. Downloading from the net !"
    try:
        #urllib.urlretrieve(sUrl,sFile)
        temp = urllib2.urlopen(sUrl)
        data = open(sFile,'wb')
        data.write(temp.read())
        data.close()
        temp.close()
        #shutil.move(temp, sFile)
        bFound = True
        #(temp, dStatus) = urllib.urlretrieve(url,file,reporthook=report)
        #print "dStatus reports "+ str(dStatus)
    #except IOError, (errno, strerror, fileattr):
        #if hasattr(X, 'Not Found'):
            #print "Got 404\n"
        #errfunc(X)
        #print "Failed\n"
    except urllib2.HTTPError, errstring:
        #if hasattr(errstring, '404'):
            #print "I got 404 page"
        print errstring
    #os.environ['FILE_DOWNLOAD'] = url
    #os.system('wget $FILE_DOWNLOAD') # In this case you require a valid .wgetrc file
    #print file," downloaded from the net\n"
    return bFound

#TODO: walk_tree_copy_debs
# This might require simplification and optimization.
# But for now it's doing the job.
# Need to find a better algorithm, maybe os.walk()                    
def walk_tree_copy_debs(sRepository, sFile, sSourceDir):
    """The core algorithm is here for the whole program to function'\n'
          It recursively searches a tree/subtree of folders for package files'\n'
          like the directory structure of "apt-proxy". If files are found (.deb || .rpm)'\n'
          it checks wether they are on the list of packages to be fetched. If yes,'\n\
          it copies them. Same goes for flat "apt archives folders" also.'\n'
          Else it fetches the package from the net"""
    bFound = False
    try:
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
def errfunc(errno):
    if errno is -3 or errno is 13:
        pass
    else:
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
            
if __name__ == "__main__":
    
    try:
        version = "0.5b"
        reldate = "03/10/2005"
        copyright = "(C) 2005 Ritesh Raj Sarraf <rrs@researchut.com>"
    
        #FIXME: Option Parsing
        # There's a flaw with either optparse or I'm not well understood with it
        # Presently you need to provide all the arguments to it to work.
        # No less, no more. This needs to be converted to getopt sometime.
        
        #parser = OptionParser()
        #parser = optparse.OptionParser()
        parser = optparse.OptionParser(usage="%prog [-d] [-s] [-u]", version="%prog " + version)
        parser.add_option("-d","--download", dest="download_path", help="Root directory path to save files", action="store", type="string")
        parser.add_option("-s","--search", dest="search_path", help="Root directory path where the pre-downloaded files will be searched. If not, give a period '.'",action="store", type="string")
        parser.add_option("-u","--uris", dest="uris_file", help="Full path of the uris file",action="store", type="string")
        (options, arguments) = parser.parse_args()
        #parser.check_required("-d", "-s", "-u")
        #if len(arguments) != 2:
        #    parser.error("Err! Incorrect number of arguments. Exiting")
        
        sSourceDir = options.download_path
        sRawUris = options.uris_file
        sRepository = options.search_path
        
        print "pypt-offline %s" % version
        print "Copyright %s" % copyright
        print """\n\nThis program is still in it's very early stage. There can be situations
        where things might not work as expected. Please direct all errors, bugs,suggestions
        etc to me at rrs@researchut.com\n\n\n"""

        # Let's first open the RAW_URIS file and read it all.
        try:
            lRawData = open(sRawUris, 'r').readlines()
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
                print sFile + " sccessfully copied from local cache.\n"
            else:        
                bStatus = download_from_web(sUrl, sFile, sSourceDir)
                if bStatus == True:
                    print sFile + " successfully downloaded from web\n."
                else:
                    print sFile + " not downloaded from web and NA in local cache.\n"
    
    except KeyboardInterrupt:
        print "\nReceived immediate EXIT signal. Exiting!\n"
