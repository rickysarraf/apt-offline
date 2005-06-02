#!/usr/bin/env python
# pypt-offline.py
# version 0.5beta

############################################################################
#    Copyright (C) 2005 by Ritesh Raj Sarraf                               #
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

import os, shutil, string, urllib, sys, getopt, optparse

def download_from_web(url, file, SOURCE_DIR):
    """Download the required file from the web"""
    """The arguments are passed everytime to the function so that, may be in future, 
        we could reuse this function"""
    os.chdir(SOURCE_DIR)
    print "\n", file," not available. Downloading from the net !"
    urllib.urlretrieve(url,file)
    ##os.environ['FILE_DOWNLOAD'] = url
    ##os.system('wget $FILE_DOWNLOAD') # In this case you require a valid .wgetrc file
    print file," downloaded from the net\n"
            
            
def walk_tree_copy_debs(REPOSITORY):
    """The core algorithm is here for the whole program to function'\n'
          It recursively searches a tree/subtree of folders for package files'\n'
          like the directory structure of "apt-proxy". If files are found (.deb || .rpm)'\n'
          it checks wether they are on the list of packages to be fetched. If yes,'\n\
          it copies them. Same goes for flat "apt archives folders" also.'\n'
          Else it fetches the package from the net"""
    for name in os.listdir(REPOSITORY):
        path = os.path.join(REPOSITORY, name)
        if os.path.isdir(path):
            walk_tree_copy_debs(path)
        elif name.endswith('.deb') or name.endswith('.rpm'):
                if name == file:
                    shutil.copy(path, SOURCE_DIR)
                    global not_available
                    not_available = 0
        else:
            global not_available
            not_available = 1
            # I know the above trick sucks
            # But I'm yet to find a better way
        
def errfunc(argument, exitcode):
    sys.stderr.write(argument)
    sys.stderr.write(" is incorrect\n")
    sys.stderr.write("Make sure path is absolute\n")
    sys.exit(exitcode)

if __name__ == "__main__":
    
    parser = optparse.OptionParser()
    
    parser.add_option("-d","--download", dest="download_path", help="Give the path where the downloaded packages will be saved", action="store", type="string")
    parser.add_option("-s","--search", dest="search_path", help="Give the path where the packages will be searched. If not, give a period '.'",action="store", type="string")
    parser.add_option("-u","--uris", dest="uris_file", help="Give the full path of the uris file",action="store", type="string")
    
    (options, arguments) = parser.parse_args()
    if os.path.isdir(options.download_path):
        SOURCE_DIR = options.download_path
    else:
        errfunc(options.download_path, 1)
        
    if os.path.isfile(options.uris_file):
        RAW_URIS = options.uris_file
    else:
        errfunc(options.uris_file, 1)
        
    if os.path.isdir(options.search_path):
        REPOSITORY = options.search_path
    elif options.search_path == '':
        REPOSITORY = os.curdir()
    else:
        errfunc(options.search_path, 1)
        
        
    version = "0.5beta"
    reldate = "03/10/2005"
    copyright = "(C) 2005 Ritesh Raj Sarraf <rrs@researchut.com>"

    print "pypt-offline %s" % version
    print "Copyright %s" % copyright
    print """\n\nThis program is still in it's very early stage. There can be situations
    where things might not work as expected. Please direct all errors, bugs,suggestions
    etc to me at rrs@researchut.com\n\n\n"""

    # Let's first open the RAW_URIS file and read it all.
    RAW_DATA = open(RAW_URIS, 'r').readlines()
    
    for each_single_item in RAW_DATA:
        SPLIT_DATA = each_single_item.split(' ') # Split on the basis of ' ' i.e. space

        # We initialize the variables "url" and "file" here.
        # We also strip the single quote character "'" to get the real data
        url = string.rstrip(string.lstrip(''.join(SPLIT_DATA[0]), chars="'"), chars="'")
        file = string.rstrip(string.lstrip(''.join(SPLIT_DATA[1]), chars="'"), chars="'")
        not_available = 0
        walk_tree_copy_debs(REPOSITORY)
        if not_available == 1:
            download_from_web(url, file, SOURCE_DIR)
