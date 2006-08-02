import os, shutil, string, sys, urllib2, pypt_progressbar, pypt_md5_check, pypt_variables, pypt_logger

'''This is the core module. It does the main job of downloading packages/update packages,\nfiguring out if the packages are in the local cache, handling exceptions and many more stuff'''

def compress_the_file(zip_file_name, files_to_compress, sSourceDir):
    '''Condenses all the files into one single file for easy transfer'''
    
    try:
        import zipfile
    except ImportError:
        log.err("Aieee!! Module not found.\n")
        
    try:
        os.chdir(sSourceDir)
    except:
        #TODO: Handle this exception
        log.err("Aieeee! I got a fatal exception that I don't understand.\nPlease debug.\n")
    
    try:
        filename = zipfile.ZipFile(zip_file_name, "a")
    except IOError:
        #INFO By design zipfile throws an IOError exception when you open
        # in "append" mode and the file is not present.
        filename = zipfile.ZipFile(zip_file_name, "w")
    except:
        #TODO Handle the exception
        log.err("\nAieee! Some error exception in creating zip file %s\n" % (zip_file_name))
        sys.exit(1)
        
    filename.write(files_to_compress, files_to_compress, zipfile.ZIP_DEFLATED)
    filename.close()
    
def decompress_the_file(file, path, filename, archive_type):
    '''Extracts all the files from a single condensed archive file'''
    
    
    if archive_type is 1:
        try:
            import bz2
        except ImportError:
            log.err("Aieeee! Module bz2 is not available.\n")
            
        try:
            fh = bz2.BZ2File(file, 'r')
        except:
            log.err("Couldn't open file %s for reading.\n" % (file))
            
        try:
            wr_fh = open (os.path.join(path, filename), 'wb')
        except:
            log.err("Couldn't open file %s at path %s for writing.\n" % (filename, path))
            
        try:
            wr_fh.write(fh.read())
        except EOFError, e:
            log.err("Bad file %s\n%s" % (file, e))
            pass
        
        wr_fh.close()
        fh.close()
        log.msg("%s file synced\n" % (filename))
        
    elif archive_type is 2:
        try:
            import gzip
        except ImportError:
            log.err("Aieee! Module gzip is not available.\n")
            
        try:
            fh = gzip.GzipFile(file, 'r')
        except:
            log.err("Couldn't open file %s for reading.\n" % (file))
            
        try:
            wr_fh = open(os.path.join(path,filename), 'wb')
        except:
            log.err("Couldn't open file %s at path %s for writing.\n" % (filename, path))
        
        try:
            wr_fh.write(fh.read())
        except EOFError, e:
            log.err("Bad file %s\n%s" % (file, e))
            pass
        
        wr_fh.close()
        fh.close()
        log.msg("%s file synced\n" % (filename))
        
    elif archive_type is 3:
        try:
            zip_file = zipfile.ZipFile(file, 'rb')
        except:
            #TODO: Handle the exceptions
            log.err("\nAieee! Some error exception in reading the zip file %s\n" % (file))
            return False
            
        for filename in zip_file.namelist():
            data = zip_file.read()
            
        zip_file.close()
    else:
        log.err("Aieeee! %s is unknown archive.\n" % (file))
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
        
        log.msg("Downloading %s\n" % (sFile))
        while i < size:
            data.write (temp.read(block_size))
            i += block_size
            counter += 1
            pypt_progressbar.myReportHook(counter, block_size, size)
        print "\n"
        data.close()
        temp.close()
        
        #INFO: Do an md5 checksum
        if pypt_variables.options.disable_md5check == True:
            pass
        else:
            if pypt_md5_check.md5_check(sFile, checksum, sSourceDir) != True:
                os.remove(sFile)
                log.err("%s checksum mismatch. File removed\n" % (sFile))
        #sys.stdout.write("%s successfully downloaded from %s\n\n" % (sFile, sUrl))
        return True
        
    #FIXME: Find out optimal fix for this exception handling
    except OSError, (errno, strerror):
        sys.stderr.write ("%s\n" %(sSourceDir))
        errfunc(errno, strerror)
        
    except urllib2.HTTPError, errstring:
        sys.stderr.write("%s\n" % (sFile))
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
            log.err("%s\n" % (e.reason))
        if hasattr(e, 'code') and hasattr(e, 'reason'):
            errfunc(e.code, e.reason)
        
#TODO: walk_tree_copy_debs - DEPRECATED
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
                            log.msg("%s is available in %s. Skipping Copy!\n" % (name, sSourceDir))
                        bFound = True
                        break
                        
                        #shutil.copy(path, sSourceDir)
                        #bFound = True
                        #break
            #return bFound
                    #return False
    except OSError, (errno, strerror):
        log.err("%s %s\n" % (errno, strerror))
        errfunc(errno, strerror)
        
        
def files(root): 
    for path, folders, files in os.walk(root): 
        for file in files: 
            yield path, file 

def copy_first_match(repository, filename, dest_dir, checksum): # aka new_walk_tree_copy() 
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
                    log.msg("%s copied from local cache %s.\n" % (file, repository))
                except shutil.Error:
                    log.msg("%s is available in %s. Skipping Copy!\n\n" % (file, dest_dir))
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
        log.err("%s\n" % (errormsg))
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
        log.err("%s - %s\n\n" % (errno, errormsg))
        #sys.stderr.write(" Will still try with other package uris\n\n")
        pass
    elif errno == 1:
        # We'll pass error code 1 where ever we want to gracefully exit
        log.err(errormsg)
        log.err("Explicit program termination %s\n" % (errno))
        sys.exit(errno)
    else:
        log.err("Aieee! I don't understand this errorcode\n" % (errno))
        sys.exit(errno)
    
def fetcher(uri, path, cache, zip_bool, zip_type_file, arg_type = 0):
    '''
    uri - The uri data whill will contain the information
    path - The path (if any) where the download needs to be done
    cache - The cache (if any) where we should check before downloading from the net
    arg_type - arg_type is basically used to identify wether it's a update download or upgrade download
    '''
    
    if arg_type == 1:
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
                    log.err("Aieeee! I couldn't create a directory")
                    errfunc(1, '')
        else:
                sSourceDir = os.path.abspath(path)
        
        if os.path.exists(os.path.join(sSourceDir, zip_type_file)):
            log.err("%s already present.\nRemove it first.\n" % (zip_type_file))
            sys.exit(1)
            
        try:
            lRawData = open(uri, 'r').readlines()
        except IOError, (errno, strerror):
            log.err("%s %s\n" % (errno, strerror))
            errfunc(errno, '')
            
        
#        #INFO: Thread Support
#        # Will require more design thoughts
#        from Queue import Queue
#        from threading import Thread, currentThread
#        
#        if pypt_variables.options.num_of_threads > 1:
#            log.msg("WARNING: Threads is still in alpha stage. It's better to use just a single thread at the moment.\n")
#            log.warn("Threads is still in alpha stage. It's better to use just a single thread at the moment.\n")
#            
#        NUMTHREADS = pypt_variables.options.num_of_threads
#        
#        def run(request, response, func=download_from_web):
#            '''Get items from the request Queue, process them
#            with func(), put the results along with the
#            Thread's name into the response Queue.
#        
#            Stop running once an item is None.'''
#        
#            name = currentThread().getName()
#            while 1:
#                item = request.get()
#                (sUrl, sFile, download_size, checksum) = stripper(item)
#                if item is None:
#                    break
#                response.put((name, func(sUrl, sFile, sSourceDir, None)))
#        
#        
#        # Create two Queues for the requests and responses
#        requestQueue = Queue()
#        responseQueue = Queue()
#        
#        
#        # Pool of NUMTHREADS Threads that run run().
#        thread_pool = [
#                       Thread(
#                              target=run,
#                              args=(requestQueue, responseQueue)
#                              )
#                       for i in range(NUMTHREADS)
#                       ]
#        
#        
#        # Start the threads.
#        for t in thread_pool: t.start()
#        
#        # Queue up the requests.
#        for item in lRawData: requestQueue.put(item)
#        
#        
#        # Shut down the threads after all requests end.
#        # (Put one None "sentinel" for each thread.)
#        for t in thread_pool: requestQueue.put(None)
#        
#        # Don't end the program prematurely.
#        #
#        # (Note that because Queue.get() is blocking by
#        # default this isn't strictly necessary.  But if
#        # you were, say, handling responses in another
#        # thread, you'd want something like this in your
#        # main thread.)
#        for t in thread_pool: t.join()
        
        for each_single_item in lRawData:
            (sUrl, sFile, download_size, checksum) = stripper(each_single_item)
            
            if download_from_web(sUrl, sFile, sSourceDir, None) != True:
                #sys.stderr.write("%s not downloaded from %s\n" % (sFile, sUrl))
                #sys.stderr.write("%s failed\n\n" % (sFile))
                #TODO: Add an errlist[] which'll keep track of all the failed url - Done
                pypt_variables.errlist.append(sFile)
                pass
            else:
                if zip_bool:
                    compress_the_file(zip_type_file, sFile, sSourceDir)
                    os.remove(sFile) # Remove it because we don't need the file once it is zipped.
                 
    if arg_type == 2:
        if path is None:
            if os.access("pypt-downloads", os.W_OK) is True:
                sSourceDir = os.path.abspath("pypt-downloads")
            else:
                try:
                    os.umask(0002)
                    os.mkdir("pypt-downloads")
                    sSourceDir = os.path.abspath("pypt-downloads")
                except:
                    log.err("Aieeee! I couldn't create a directory")
        else:
            sSourceDir = os.path.abspath(path)
            
        if os.path.exists(os.path.join(sSourceDir, zip_type_file)):
            log.err("%s already present.\nRemove it first.\n" % (zip_type_file))
            sys.exit(1)
                
        if cache is not None:
            cache = os.path.abspath(cache)
            
        try:
            lRawData = open(uri, 'r').readlines()
        except IOError, (errno, strerror):
            log.err("%s %s\n" %(errno, strerror))
            errfunc(errno, '')
        
        for each_single_item in lRawData:
            (sUrl, sFile, download_size, checksum) = stripper(each_single_item)
            
            if cache is None:
                if download_from_web(sUrl, sFile, sSourceDir, checksum) != True:
                    #sys.stderr.write("%s not downloaded from %s and NA in local cache %s\n\n" % (sFile, sUrl, sRepository))
                    pypt_variables.errlist.append(sFile)
                    if zip_bool:
                        compress_the_file(zip_type_file, sFile, sSourceDir)
                        os.unlink(sFile)
                        
            else:
                if copy_first_match(cache, sFile, sSourceDir, checksum) == False:
                    if download_from_web(sUrl, sFile, sSourceDir, checksum) != True:
                         #sys.stderr.write("%s not downloaded from %s and NA in local cache %s\n\n" % (sFile, sUrl, sRepository))
                         pypt_variables.errlist.append(sFile)
                    else:
                        if os.path.exists(os.path.join(cache, sFile)):
                            #INFO: The file is already there.
                            pass
                        else:
                            shutil.copy(sFile, cache)
                                
                        if zip_bool:
                            compress_the_file(zip_type_file, sFile, sSourceDir)
                            os.unlink(sFile)
                elif True:
                    if zip_bool:
                        compress_the_file(zip_type_file, sFile, sSourceDir)
                        os.unlink(sFile)
                        
    for error in pypt_variables.errlist:
        log.err("%s failed.\n" % (error))
        #zip_the_file("pypt-offline-upgrade-fetched.zip", sSourceDir) 
        
def syncer(install_file_path, target_path, arg_type=None):
    '''Syncer does the work of syncing the downloaded files.
    It syncs "install_file_path" which could be a valid file path
    or a zip archive to "target_path'''
    
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
            
            if pypt_magic.file(os.path.abspath(filename)) == "application/x-bzip2":
                decompress_the_file(os.path.abspath(filename), target_path, filename, 1)
            elif pypt_magic.file(os.path.abspath(filename)) == "application/x-gzip":
                decompress_the_file(os.path.abspath(filename), target_path, filename, 2)
            elif pypt_magic.file(filename) == "PGP armored data":
                try:
                    shutil.copy(filename, target_path)
                    log.msg("%s file synced.\n" % (filename))
                except shutil.Error:
                    log.err("%s is already present.\n" % (filename))
            elif pypt_magic.file(filename) == "application/x-dpkg":
                try:
                    shutil.copy(filename, target_path)
                    log.msg("%s file synced.\n" % (filename))
                except shutil.Error:
                    log.err("%s is already present.\n" % (filename))
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
                decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 1)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/gzip":
                decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 2)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "application/zip":
                decompress_the_file(os.path.join(install_file_path, eachfile), target_path, eachfile, 3)
            elif pypt_magic.file(os.path.join(install_file_path, eachfile)) == "PGP armored data":
                try:
                    shutil.copy(os.path.join(install_file_path, eachfile), target_path)
                    log.msg("%s file synced.\n" % (eachfile))
                except shutil.Error:
                    log.err("%s is already present.\n" % (filename))
            elif pypt_magic.file(filename) == "application/x-dpkg":
                try:
                    shutil.copy(filename, target_path)
                    log.msg("%s file synced.\n" % (filename))
                except shutil.Error:
                    log.err("%s is already present.\n" % (filename))
            else:
                log.err("Aieeee! I don't understand filetype %s\n" % (eachfile))
                
def main():
    # Okay!! We got all the options and arguments.
    # Now let's begin....
    
    try:
        # The log implementation
        # Instantiate the class
        global log
        log = pypt_logger.log(pypt_variables.options.warnings, pypt_variables.options.verbose, pypt_variables.options.debug)
        
        log.msg("pypt-offline %s\n" % (pypt_variables.version))
        log.msg("Copyright %s\n" % (pypt_variables.copyright))
        
        if pypt_variables.options.set_update:
            if sys.platform in pypt_variables.supported_platforms:
                if os.geteuid() != 0:
                    parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                else:
                    log.msg("Generating database of files that are needed for an update.\n")
                    os.environ['__pypt_set_update'] = pypt_variables.options.set_update
                    if os.system('/usr/bin/apt-get -qq --print-uris update > $__pypt_set_update') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
            else:
                 parser.error("This argument is supported only on Unix like systems with apt installed\n")
            sys.exit(0)
     
        if pypt_variables.options.set_upgrade or pypt_variables.options.upgrade_type:
            if not (pypt_variables.options.set_upgrade and pypt_variables.options.upgrade_type):
                parser.error("Options --set-upgrade and --upgrade-type are mutually inclusive\n")
                     
            if sys.platform in pypt_variables.supported_platforms:
                if os.geteuid() != 0:
                    parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                #TODO: Use a more Pythonic way for it
                if pypt_variables.options.upgrade_type == "upgrade":
                    log.msg("Generating database of files that are needed for an upgrade.\n")
                    os.environ['__pypt_set_upgrade'] = pypt_variables.options.set_upgrade
                    if os.system('/usr/bin/apt-get -qq --print-uris upgrade > $__pypt_set_upgrade') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
                elif pypt_variables.options.upgrade_type == "dist-upgrade":
                    log.msg("Generating database of files that are needed for a dist-upgrade.\n")
                    os.environ['__pypt_set_upgrade'] = pypt_variables.options.set_upgrade
                    if os.system('/usr/bin/apt-get -qq --print-uris dist-upgrade > $__pypt_set_upgrade') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
                elif pypt_variables.options.upgrade_type == "dselect-upgrade":
                    log.msg("Generating database of files that are needed for a dselect-upgrade.\n")
                    os.environ['__pypt_set_upgrade'] = pypt_variables.options.set_upgrade
                    if os.system('/usr/bin/apt-get -qq --print-uris dselect-upgrade > $__pypt_set_upgrade') != 0:
                        log.err("FATAL: Something is wrong with the apt system.\n")
                else:
                    parser.error("Invalid upgrade argument type selected\nPlease use one of, upgrade/dist-upgrade/dselect-upgrade\n")
            else:
                parser.error("This argument is supported only on Unix like systems with apt installed\n")
                sys.exit(0)
                 
        if pypt_variables.options.set_install_packages or pypt_variables.options.set_install:
            if not (pypt_variables.options.set_install_packages and pypt_variables.options.set_install):
                parser.error("Options --set-install and --set-install-package are mutually inclusive\n")
                
            if sys.platform in pypt_variables.supported_platforms:
                if os.geteuid() != 0:
                    parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                    
                log.msg("Generating database of the package and its dependencies.\n")
                os.environ['__pypt_set_install'] = pypt_variables.options.set_install
                os.environ['__pypt_set_install_packages'] = ''
                
                #INFO: This is improper way of getting the args, the name of the packages.
                # But since optparse doesn't have the implementation in place at the moment, we're using it.
                # Once fixed, this will be changed.
                # For details look at the parser.add_option line above.
                for x in pypt_variables.args:
                    os.environ['__pypt_set_install_packages'] += x + ' '
                    
                #FIXME: Find a more Pythonic implementation
                if os.system('/usr/bin/apt-get -qq --print-uris install $__pypt_set_install_packages > $__pypt_set_install') != 0:
                    log.err("FATAL: Something is wrong with the apt system.\n")
            else:
                parser.error("This argument is supported only on Unix like systems with apt installed\n")
                sys.exit(0)
               
        if pypt_variables.options.fetch_update:
            log.msg("\nFetching uris which update apt's package database\n\n")
           
            pypt_variables.options.disable_md5check = True
            # Since we're in fetch_update, the download_type will be non-deb/rpm data
            # 1 is for update packages 
            # 2 is for upgrade packages
            fetcher(pypt_variables.options.fetch_update, pypt_variables.options.download_dir, pypt_variables.options.cache_dir, pypt_variables.options.zip_it, pypt_variables.options.zip_update_file, 1)
                 
        if pypt_variables.options.fetch_upgrade:
            log.msg("\nFetching packages which need upgradation\n\n")
                 
            # Since we're in fetch_update, the download_type will be non-deb/rpm data
            # 1 is for update packages 
            # 2 is for upgrade packages
            fetcher(pypt_variables.options.fetch_upgrade, pypt_variables.options.download_dir, pypt_variables.options.cache_dir, pypt_variables.options.zip_it, pypt_variables.options.zip_upgrade_file, 2)
            sys.exit(0)
                 
        if pypt_variables.options.install_update:
            #INFO: Comment these lines to do testing on Windows machines too
            if os.geteuid() != 0:
                log.err("\nYou need superuser privileges to execute this option\n")
                sys.exit(1)
                
            if os.path.isfile(pypt_variables.options.install_update) is True:
                # Okay! We're a file. It should be a zip file
                syncer(pypt_variables.options.install_update, pypt_variables.apt_update_target_path, 1)
            elif os.path.isdir(pypt_variables.options.install_update) is True:
                # We're a directory
                syncer(pypt_variables.options.install_update, pypt_variables.apt_update_target_path, 2)
            else:
                log.err("Aieee! %s is unsupported format\n" % (pypt_variables.options.install_update))
            sys.exit(0)
            
        if pypt_variables.options.install_upgrade:
            #INFO: Comment these lines to do testing on Windows machines too
            if os.geteuid() != 0:
                log.err("\nYou need superuser privileges to execute this option\n")
                sys.exit(1)
            if os.path.isfile(pypt_variables.options.install_upgrade) is True:
                syncer(pypt_variables.options.install_upgrade, pypt_variables.apt_package_target_path, 1)
            elif os.path.isdir(pypt_variables.options.install_upgrade) is True:
                syncer(pypt_variables.options.install_upgrade, pypt_variables.apt_package_target_path, 2)
            else:
                log.err("Aieee! %s is unsupported format\n" % (pypt_variables.options.install_upgrade))
            sys.exit(0)
            
    except KeyboardInterrupt:
        log.err("\nInterrupted by user. Exiting!\n")
        sys.exit(1)        
            
if __name__ == "__main__":
    main()