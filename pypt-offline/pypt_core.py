import os, shutil, string, sys, progressbar, urllib2, pypt_md5_check, pypt_variables

'''This is the core module. It does the main job of downloading packages/update packages,\nfiguring out if the packages are in the local cache, handling exceptions and many more stuff'''

def compress_the_file(zip_file_name, files_to_compress, sSourceDir):
    '''Condenses all the files into one single file for easy transfer'''
    
    try:
        import zipfile
    except ImportError:
        sys.stderr.write("Aieeee! module not found.\n")
        
    try:
        os.chdir(sSourceDir)
    except:
        #TODO: Handle this exception
        pass
    
    try:
        filename = zipfile.ZipFile(zip_file_name, "a")
    except IOError:
        #INFO By design zipfile throws an IOError exception when you open
        # in "append" mode and the file is not present.
        filename = zipfile.ZipFile(zip_file_name, "w")
    except:
        #TODO Handle the exception
        sys.stderr.write("\nAieee! Some error exception in creating zip file %s\n" % (zip_file_name))
        sys.exit(1)
        
    #zip_file.write(filename, os.path.basename(filename))
    filename.write(files_to_compress, files_to_compress, zipfile.ZIP_DEFLATED)
    filename.close()
    
def decompress_the_file(file, path, filename, archive_type):
    '''Extracts all the files from a single condensed archive file'''
    
    
    if archive_type is 1:
        try:
            import bz2
        except ImportError:
            sys.stderr.write("Aieeee! Module bz2 is not available.\n")
        try:
            fh = bz2.BZ2File(file, 'r')
        except:
            sys.stderr.write("Couldn't open file %s for reading.\n" % (file))
        try:
            os.chdir(path)
        except:
            sys.stderr.write("Couldn't chdir() to %s.\n" % (path_))
        try:
            wr_fh = open (filename, 'wb')
        except:
            sys.stderr.write("Couldn't open file %s at path %s for writing.\n" % (filename, path))
        try:
            wr_fh.write(fh.read())
        except EOFError, e:
            sys.stderr.write("Bad file %s\n%s" % (file, e))
            pass
        wr_fh.close()
        fh.close()
        sys.stdout.write("%s file synced\n" % (filename))
    elif archive_type is 2:
        pass
    elif archive_type is 3:
        try:
            zip_file = zipfile.ZipFile(file, 'rb')
        except:
            #TODO: Handle the exceptions
            sys.stderr.write("\nAieee! Some error exception in reading the zip file %s\n" % (file))
            return False
            
        for filename in zip_file.namelist():
            data = zip_file.read()
            
        zip_file.close()
    else:
        sys.stderr.write("Aieeee! %s is unknown archive.\n" % (file))
        return False
        
    return True

def download_from_web(sUrl, sFile, sSourceDir, checksum):
    '''
    Download the required file from the web
    The arguments are passed everytime to the function so that,
    may be in future, we could reuse this function
    '''
       
    try:
        block_size = 4096
        i = 0
        counter = 0
        
        os.chdir(sSourceDir)
        temp = urllib2.urlopen(sUrl)
        headers = temp.info()
        size = int(headers['Content-Length'])
        data = open(sFile,'wb')
        
        sys.stdout.write("Downloading %s\n" % (sFile))
        while i < size:
            data.write (temp.read(block_size))
            i += block_size
            counter += 1
            progressbar.myReportHook(counter, block_size, size)
        print "\n"
        data.close()
        temp.close()
        
        #INFO: Do an md5 checksum
        if pypt_variables.options.disable_md5check == True:
            pass
        else:
            if pypt_md5_check.md5_check(sFile, checksum, sSourceDir) != True:
                os.remove(sFile)
                sys.stderr.write("%s checksum mismatch. File removed\n" % (sFile))
        #sys.stdout.write("%s successfully downloaded from %s\n\n" % (sFile, sUrl))
        return True
        
    #FIXME: Find out optimal fix for this exception handling
    except OSError, (errno, strerror):
        sys.stderr.write ("%s\n" %(sSourceDir))
        errfunc(errno, strerror)
        
    except urllib2.HTTPError, errstring:
        errfunc(errstring.code, errstring.msg)
        
    except urllib2.URLError, errstring:
        #We pass error code "1" here becuase URLError
        # doesn't pass any error code.
        # URLErrors shouldn't be ignored, hence program termination
        if errstring.reason.args[0] == 10060:
            errfunc(errstring.reason.args[0], errstring.reason)
        #errfunc(1, errstring.reason)
        #pass
    
    except IOError, e:
        if hasattr(e, 'reason'):
            sys.stderr.write("%s\n" % (e.reason))
        if hasattr(e, 'code') and hasattr(e, 'reason'):
            errfunc(e.code, e.reason)
        
    #return bFound

#TODO: walk_tree_copy_debs

# This might require simplification and optimization.
# But for now it's doing the job.
# Need to find a better algorithm, maybe os.walk()                    
def walk_tree_copy_debs(sRepository, sFile, sSourceDir):
    '''
    This function checks for a package to see if its already downloaded
    It can search directories with depths.
    '''
    #The core algorithm is here for the whole program to function'\n'
    #It recursively searches a tree/subtree of folders for package files'\n'
    #like the directory structure of "apt-proxy". If files are found (.deb || .rpm)'\n'
    #it checks wether they are on the list of packages to be fetched. If yes,'\n\
    #it copies them. Same goes for flat "apt archives folders" also.'\n'
    #Else it fetches the package from the net"""
    bFound = False
    try:
        if sRepository is not None:
            for name in os.listdir(sRepository) and bFound == True:
                #if bFound == True:
                #    break
                path = os.path.join(sRepository, name)
                if os.path.isdir(path):
                    walk_tree_copy_debs(path, sFile, sSourceDir)
                    #walk_tree_copy_debs(path, sFile)
                elif name.endswith('.deb') or name.endswith('.rpm'):
                    if name == sFile:
                        try:
                            shutil.copy(path, sSourceDir)
                        except IOError, (errno, errstring):
                            errfunc(errno, errstring)
                        except shutil.Error:
                            sys.stdout.write("%s is available in %s. Skipping Copy!\n" % (name, sSourceDir))
                        bFound = True
                        break
                        
                        #shutil.copy(path, sSourceDir)
                        #bFound = True
                        #break
            #return bFound
                    #return False
    except OSError, (errno, strerror):
        sys.stderr.write("%s %s\n" % (errno, strerror))
        errfunc(errno, strerror)
        
        
def files(root): 
    for path, folders, files in os.walk(root): 
        for file in files: 
            yield path, file 

def copy_first_match(repository, filename, dest_dir, checksum): # aka walk_tree_copy() 
    '''Walks into "reposiotry" looking for "filename".
    If found, copies it to "dest_dir" but first verifies their md5 "checksum".'''
    for path, file in files(repository): 
        if file == filename:
            #INFO: md5check is compulsory here
            # There's no point in checking for the disable-md5 option because
            # copying a damaged file is of no use
            if pypt_md5_check.md5_check(file, checksum, path) == True:
               try:
                  shutil.copy(os.path.join(path, file), dest_dir)
                  sys.stdout.write("%s copied from local cache %s.\n" % (file, repository))
               except shutil.Error:
                  sys.stdout.write("%s is available in %s. Skipping Copy!\n\n" % (file, dest_dir))
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
    size = string.rstrip(string.lstrip(''.join(item[2]), chars = "'"), chars="'")
    #INFO: md5 ends up having '\n' with it.
    # That needs to be stripped too.
    md5_text = string.rstrip(string.lstrip(''.join(item[3]), chars = "'"), chars = "'")
    md5_text = string.rstrip(md5_text, chars = "\n")
    
    return url, file, size, md5_text


def errfunc(errno, errormsg):
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
    
    if errno == -3 or errno == 13:
        #TODO: Find out what these error codes are for
        # and better document them the next time you find it out.
        # 13 is for "Permission Denied" when you don't have privileges to access the destination 
        pass
    elif errno == 407 or errno == 2:
        # These, I believe are from OSError/IOError exception.
        # I'll document it as soon as I confirm it.
        sys.stderr.write("%s\n" % (errormsg))
        sys.exit(errno)
    elif errno == 504 or errno == 404 or errno == 10060:
        #TODO: Counter which will inform that some packages weren't fetched.
        # A counter needs to be implemented which will at the end inform the list of sources which 
        # failed to be downloaded with the above codes.
        
        # 504 is for gateway timeout
        # On gateway timeouts we can keep trying out becuase
        # one apt source.list might have different hosts.
        # 404 is for URL error. Page not found.
        # THere can be instances where one source is changed but the rest are working.
        # 10060 is for Operation Time out. There can be multiple reasons for this timeout
        # Primarily if the host is down or a slow network or abruption, hence not the whole execution should be aborted
        sys.stderr.write("%s %s\n" % (errno, errormsg))
        sys.stderr.write("Will still try with other package uris\n")
        pass
    elif errno == 1:
        # We'll pass error code 1 where ever we want to gracefully exit
        sys.stderr.write(errormsg)
        sys.stderr.write("Explicit program termination %s\n" % (errno))
        sys.exit(errno)
    else:
        sys.stderr.write("Aieee! I don't understand this errorcode\n" % (errno))
        sys.exit(errno)
    
def fetcher(uri, path, cache, zip_bool, zip_type_file, type = 0):
    '''
    uri - The uri data whill will contain the information
    path - The path (if any) where the download needs to be done
    cache - The cache (if any) where we should check before downloading from the net
    type - type is basically used to identify wether it's a update download or upgrade download
    '''
    
    if type == 1:
        #INFO: Oh! We're only downloading the update package list database
        # Package Update database changes almost daily in Debian.
        # This is at least true for Sid. Hence it doesn't make sense to copy
        # update packages' database from a cache.
        
        if path is None:
            if os.access("pypt-downloads", os.W_OK) is True:
                sSourceDir = os.path.abspath("pypt-downloads")
            else:
                try:
                    os.umask(0002)
                    os.mkdir("pypt-downloads")
                    sSourceDir = os.path.abspath("pypt-downloads")
                except:
                    sys.stderr.write("Aieeee! I couldn't create a directory")
                    errfunc(1)
        else:
                sSourceDir = path
        
        try:
            lRawData = open(uri, 'r').readlines()
        except IOError, (errno, strerror):
            sys.stderr.write("%s %s\n" % (errno, strerror))
            errfunc(errno)
            
        #if options.zip_it:
        #    zip_update_file = options.zip_update_file
        
        for each_single_item in lRawData:
            (sUrl, sFile, download_size, checksum) = stripper(each_single_item)
            
            #bStatus = download_from_web(sUrl, sFile, sSourceDir)
            #if bStatus != True:
            #     sys.stdout.write("%s not downloaded from %s\n" % (sFile, sUrl))
            if download_from_web(sUrl, sFile, sSourceDir, None) != True:
                sys.stderr.write("%s not downloaded from %s\n" % (sFile, sUrl))
            else:
                if zip_bool:
                    compress_the_file(zip_type_file, sFile, sSourceDir)
                    os.remove(sFile) # Remove it because we don't need the file once it is zipped.
                 
    if type == 2:
        if path is None:
            if os.access("pypt-downloads", os.W_OK) is True:
                sSourceDir = os.path.abspath("pypt-downloads")
            else:
                try:
                    os.umask(0002)
                    os.mkdir("pypt-downloads")
                    sSourceDir = os.path.abspath("pypt-downloads")
                except:
                    sys.stderr.write("Aieeee! I couldn't create a directory")
        else:
            sSourceDir = path
                
        if cache is None:
            sRepository = os.path.abspath(os.curdir)
        else:
            sRepository = cache
            
        try:
            lRawData = open(uri, 'r').readlines()
        except IOError, (errno, strerror):
            sys.stderr.write("%s %s\n" %(errno, strerror))
            errfunc(errno)
        
        for each_single_item in lRawData:
            (sUrl, sFile, download_size, checksum) = stripper(each_single_item)
                     
            if copy_first_match(sRepository, sFile, sSourceDir, checksum) == False:
                if download_from_web(sUrl, sFile, sSourceDir, checksum) != True:
                     sys.stderr.write("%s not downloaded from %s and NA in local cache %s\n\n" % (sFile, sUrl, sRepository))
                else:
                    if zip_bool:
                        compress_the_file(zip_type_file, sFile, sSourceDir)
            elif True:
                if zip_bool:
                    compress_the_file(zip_type_file, sFile, sSourceDir)
                        
        #zip_the_file("pypt-offline-upgrade-fetched.zip", sSourceDir) 
        
def syncer(install_file_path, target_path, type=None):
    '''Syncer does the work of syncing the downloaded files.
    It syncs "install_file_path" which could be a valid file path
    or a zip archive to "target_path'''
    
    if type == 1:
        try:
            import zipfile
        except ImportError:
            sys.stderr.write("Aieeee! Module zipfile not found.\n")
            sys.exit(1)
            
        file = zipfile.ZipFile(install_file_path, "r")
        for filename in file.namelist():
            try:
                import pypt_magic
            except ImportError:
                sys.stderr.write("Aieeee! Module pypt_magic not found.\n")
                sys.exit(1)
            data = open(filename, "wb")
            data.write(file.read(filename))
            data.close()
            #data = file.read(filename)
            if pypt_magic.file(filename) == "application/x-bzip2":
                decompress_the_file(os.path.abspath(filename), target_path, filename, 1)
            elif pypt_magic.file(filename) == "PGP armored data":
                try:
                    shutil.copy(filename, target_path)
                    sys.stdout.write("%s file synced.\n" % (filename))
                except shutil.Error:
                    sys.stderr.write("%s is already present.\n" % (filename))
                
    elif type == 2:
        for eachfile in os.listdir(install_file_path):
            
            archive_file_types = ['application/x-bzip2', 'application/gzip', 'application/zip']
            archive_type = None
            try:
                import pypt_magic
            except ImportError:
                sys.stderr.write("Aieeee! module not found.\n")
                
            if pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/x-bzip2":
                decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 1)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/gzip":
                decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 2)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/zip":
                decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 3)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "PGP armored data":
                shutil.copy(os.path.join(install_file_path, eachfile), target_path)
                sys.stdout.write("%s file synced.\n" % (eachfile))
            else:
                sys.stderr.write("Aieeee! I don't understand filetype %s\n" % (eachfile))
                
        