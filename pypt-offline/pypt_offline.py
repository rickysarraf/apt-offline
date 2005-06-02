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

import os, shutil, string, urllib, sys, getopt

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
            
            
def walk_trgetoptee_copy_debs(REPOSITORY):
     """The core algorithm is here for the whole program to function'\n'
          It recursively searches a tree/subtree of folders for package files'\n'
          like the directory structure of "apt-proxy". If files are found (.deb || .rpm)'\n'
          it checks wether they are on the list of packages to be fetched. If yes,'\n\
          it copies them. Same goes for flat "apt archives folders" also.'\n'
          Else it fetches the package from the net"""
     if os.listdir(REPOSITORY) == []:
        download_from_web(url, file, SOURCE_DIR)
     else:
        for name in os.listdir(REPOSITORY):
            path = os.path.join(REPOSITORY, name)
            if os.path.isdir(path):
                walk_tree_copy_debs(path)
            elif name.endswith('.deb') or name.endswith('.rpm'):
                if name == file:
                    shutil.copy(file, SOURCE_DIR)
            else:
                download_from_web(url,file, SOURCE_DIR)

def usage(exitcode):
    sys.stderr.write("Usage: pypt_offline [options]\n")
    sys.stderr.write("Example: pypt_offline --download = /tmp/ --search = /var/cache/apt-archives/ --uris = /mnt/usb/uris\n")
    sys.exit(exitcode)

if __name__ == "__main__":
    
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'd:s:u:h:', ['download=', 'search=', 'uris=', 'help'])
    except getopt.GetoptError:
        usage(1)

    if len(args) < 1:
        usage(1)
    
    foreach opt, args in optlist:
        if opt in ('-d', '--download'):
            print "I'm in download"
        elif opt in ('-s', '--search'):
            print "I'm in search"
        elif opt in ('-u', '--uris'):
            print "I'm in uris"
        elif opt in ('-h', '--help'):
            print "I'm in help"
    
    version = "0.5beta"
    reldate = "03/10/2005"
    copyright = "(C) 2005 Ritesh Raj Sarraf <rrs@researchut.com>"

    print "pypt-offline %s" % version
    print "Copyright %s" % copyright
    print """\n\nThis program is still in it's very early stage. There can be situations
    where things might not work as expected. Please direct all errors, bugs,suggestions
    etc to me at rrs@researchut.com\n\n\n"""

    print "Enter the directory where the downloaded files will be saved."
    SOURCE_DIR = raw_input()
    
    print "Enter the path where the uris file is. Eg: /mnt/usb/uris."
    RAW_URIS = raw_input()
    # This is the file on which we are based,
    # The output from `apt-get -qq --print-uris dist-upgrade > uris`

    # Let's first open the RAW_URIS file and read it all.
    RAW_DATA = open(RAW_URIS, 'r').readlines()

    print "Enter the apt repository where, the already downloaded, packages can be searched."
    print "Press \"Enter\" key for none.\n"
    REPOSITORY = raw_input()
    if REPOSITORY is '':
        REPOSITORY = os.curdir
    
    for each_single_item in RAW_DATA:
        SPLIT_DATA = each_single_item.split(' ') # Split on the basis of ' ' i.e. space

        # We initialize the variables "url" and "file" here.
        # We also strip the single quote character "'" to get the real data
        url = string.rstrip(string.lstrip(''.join(SPLIT_DATA[0:1]), chars="'"), chars="'")
        file = string.rstrip(string.lstrip(''.join(SPLIT_DATA[1:2]), chars="'"), chars="'")
        walk_tree_copy_debs(REPOSITORY)
        
