import os, sys, optparse, pypt_core

"""Contains most of the variables that are required by the application to run.
Also does command-line option parsing and variable validation."""

try:
   version = "0.6.Beta"
   reldate = "07/07/2006"
   copyright = "(C) 2005 Ritesh Raj Sarraf - RESEARCHUT (http://www.researchut.com/)"
        
   errlist = []
   supported_platforms = ["linux2", "gnu0", "gnukfreebsd5"]
   apt_update_target_path = '/var/lib/apt/lists/'
   apt_package_target_path = '/var/cache/apt/archives/'
   # Dummy paths while testing on Windows
   #apt_update_target_path = 'C:\\temp'
   #apt_package_target_path = 'C:\\temp'
   
   #FIXME: Option Parsing
   # There's a flaw with either optparse or I'm not well understood with it
   # Presently you need to provide all the arguments to it to work.
   # No less, no more. This needs to be converted to getopt sometime.
   #FIXME: Another fixme
   #parser = OptionParser()
   #parser = optparse.OptionParser()
   parser = optparse.OptionParser(usage="%prog [OPTION1, OPTION2, ...]", version="%prog " + version + "\n" + copyright)
   parser.add_option("-d","--download-dir", dest="download_dir", help="Root directory path to save the downloaded files", action="store", type="string", metavar="pypt-downloads")
   #parser.set_defaults(download_dir="pypt-downloads")
   parser.add_option("-s","--cache-dir", dest="cache_dir", help="Root directory path where the pre-downloaded files will be searched. If not, give a period '.'",action="store", type="string", metavar=".")
   #parser.set_defaults(cache_dir=".")
   #parser.set_defaults(cache_dir=".")
   parser.add_option("-u","--uris", dest="uris_file", help="Full path of the uris file which contains the main database of files to be downloaded",action="store", type="string")
   parser.add_option("","--disable-md5check", dest="disable_md5check", help="Disable md5checksum validation on downloaded files", action="store_true")
   parser.add_option("-z","--zip", dest="zip_it", help="Zip the downloaded files to a single zip file", action="store_true")
   parser.add_option("--zip-update-file", dest="zip_update_file", help="Default zip file for downloaded (update) data", action="store", type="string", metavar="pypt-offline-update.zip", default="pypt-offline-update.zip")
   parser.add_option("--zip-upgrade-file", dest="zip_upgrade_file", help="Default zip file for downloaded (upgrade) data", action="store", type="string", metavar="pypt-offline-upgrade.zip", default="pypt-offline-upgrade.zip")
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
   #parser.add_option("", "--set-install", dest="set_install", help="Extract the list of uris which need to be fetched for installation of the given package and its dependencies", action="store", type="string", nargs=10, metavar="package_name")
   parser.add_option("", "--set-install", dest="set_install", help="Extract the list of uris which need to be fetched for installation of the given package and its dependencies", action="store_true", metavar="package_names")
   parser.add_option("","--set-update", dest="set_update", help="Extract the list of uris which need to be fetched for updation", action="store", type="string", metavar="pypt-offline-update.dat")
   #parser.set_defaults(set_update="pypt-offline-update.dat")
   parser.add_option("","--fetch-update", dest="fetch_update", help="Fetch the list of uris which are needed for apt's databases _updation_. This command must be executed on the WITHNET machine", action="store", type="string", metavar="pypt-offline-update.dat")
   #parser.set_defaults(fetch_update="pypt-offline-update.dat")
   parser.add_option("","--install-update", dest="install_update", help="Install the fetched database files to the  NONET machine and _update_ the apt database on the NONET machine. This command must be executed on the NONET machine", action="store", type="string", metavar="pypt-offline-update.zip")
   #parser.set_defaults(install_update="pypt-offline-update-fetched.zip")
   parser.add_option("","--set-upgrade", dest="set_upgrade", help="Extract the list of uris which need to be fetched for _upgradation_", action="store", type="string", metavar="pypt-offline-upgrade.dat")
   #parser.set_defaults(set_upgrade="pypt-offline-upgrade.dat")
   parser.add_option("","--upgrade-type", dest="upgrade_type", help="Type of upgrade to do. Use one of upgrade, dist-upgrade, dselect-ugprade", action="store", type="string", metavar="upgrade")
   #parser.set_defaults(upgrade_type="upgrade")
   parser.add_option("","--fetch-upgrade", dest="fetch_upgrade", help="Fetch the list of uris which are needed for apt's databases _upgradation_. This command must be executed on the WITHNET machine", action="store", type="string", metavar="pypt-offline-upgrade.dat")
   #parser.set_defaults(fetch_upgrade="pypt-offline-upgrade.dat")
   parser.add_option("","--install-upgrade", dest="install_upgrade", help="Install the fetched packages to the  NONET machine and _upgrade_ the packages on the NONET machine. This command must be executed on the NONET machine", action="store", type="string", metavar="pypt-offline-upgrade.zip")
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
        
#  if options.zip_it:
#  zip_it = options.zip_it
#  zip_update_file = options.zip_update_file
#  zip_upgrade_file = options.zip_upgrade_file
#            
   sys.stdout.write("pypt-offline %s\n" % (version))
   sys.stdout.write("Copyright %s\n" % (copyright))
        
   if options.set_update:
        #if sys.platform == "linux2" or sys.platform == "gnu0" or sys.platform == "gnukfreebsd5":
        if sys.platform in supported_platforms:
            if os.geteuid() != 0:
                parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
                    
            else:
                sys.stdout.write("Generating database of files that are needed for an update.\n")
                os.chdir(options.set_update)
                os.system('/usr/bin/apt-get -qq --print-uris update > pypt-offline-update.dat')
        else:
            parser.error("This argument is supported only on Unix like systems with apt installed\n")
        sys.exit(0)

   if options.set_upgrade or options.upgrade_type:
       if not (options.set_upgrade and options.upgrade_type):
           parser.error("Options --set-upgrade and --upgrade-type are mutually inclusive\n")
                
       if sys.platform in supported_platforms:
           if os.geteuid() != 0:
               parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
           #TODO: Use a more Pythonic way for it
           if options.upgrade_type == "upgrade":
               sys.stdout.write("Generating database of files that are needed for an upgrade.\n")
               os.system('/usr/bin/apt-get -qq --print-uris upgrade > pypt-offline-upgrade.data')
           elif options.upgrade_type == "dist-upgrade":
              sys.stdout.write("Generating database of files that are needed for an upgrade.\n")
              os.system('/usr/bin/apt-get -qq --print-uris dist-upgrade > pypt-offline-upgrade.data')
           elif options.upgrade_type == "dselect-upgrade":
              sys.stdout.write("Generating database of files that are needed for an upgrade.\n")
              os.system('/usr/bin/apt-get -qq --print-uris dselect-upgrade > pypt-offline-upgrade.data')
           else:
              parser.error("Invalid upgrade argument type selected\nPlease use one of, upgrade/dist-upgrade/dselect-upgrade\n")
       else:
          parser.error("This argument is supported only on Unix like systems with apt installed\n")
          sys.exit(0)
            
   if options.set_install:
       if sys.paltform in supported_platforms:
           if os.geteuid() != 0:
               parser.error("This option requires super-user privileges. Execute as root or use sudo/su")
           sys.stdout.write("Generating database of the package and its dependencies.\n")
           os.environ['__pypt_set_install'] = ''
           for x in args:
               os.environ['__pypt_set_install'] += x + ' '
           #FIXME: Find a more Pythonic implementation
           os.system('/usr/bin/apt-get -qq --print-uris install $__pypt_set_install > pypt-offline-install.dat')
       else:
          parser.error("This argument is supported only on Unix like systems with apt installed\n")
          sys.exit(0)
           
   if options.fetch_update:
      sys.stdout.write("\nFetching uris which update apt's package database\n\n")
      
      options.disable_md5check = True
      # Since we're in fetch_update, the download_type will be non-deb/rpm data
      # 1 is for update packages 
      # 2 is for upgrade packages
      pypt_core.fetcher(options.fetch_update, options.download_dir, options.cache_dir, options.zip_it, options.zip_update_file, 1)
            
   if options.fetch_upgrade:
      sys.stdout.write("\nFetching packages which need upgradation\n\n")
            
      # Since we're in fetch_update, the download_type will be non-deb/rpm data
      # 1 is for update packages 
      # 2 is for upgrade packages
      pypt_core.fetcher(options.fetch_upgrade, options.download_dir, options.cache_dir, options.zip_it, options.zip_upgrade_file, 2)
      sys.exit(0)
            
   if options.install_update:
       #TODO: Comment these lines to do testing on Windows machines too
       if os.geteuid() != 0:
           sys.stderr.write("\nYou need superuser privileges to execute this option\n")
           sys.exit(1)
       if os.path.isfile(options.install_update) is True:
           # Okay! We're a file. It should be a zip file
           pypt_core.syncer(options.install_update, apt_update_target_path, 1)
       elif os.path.isdir(options.install_update) is True:
           # We're a directory
           pypt_core.syncer(options.install_update, apt_update_target_path, 2)
       else:
           sys.stderr.write("Aieee! %s is unsupported format\n" % (options.install_update))
       sys.exit(0)
       #pypt_core.syncer(options.install_update, apt_update_target_path, 1)
       #if pypt_core.unzip_the_file(options.install_update, apt_update_target_path) == False:
       
   if options.install_upgrade:
       #TODO: Comment these lines to do testing on Windows machines too
       if os.geteuid() != 0:
           sys.stderr.write("\nYou need superuser privileges to execute this option\n")
           sys.exit(1)
       if os.path.isfile(options.install_upgrade) is True:
           pypt_core.syncer(options.install_upgrade, apt_package_target_path, 1)
       elif os.path.isdir(options.install_upgrade) is True:
           pypt_core.syncer(options.install_upgrade, apt_package_target_path, 2)
       else:
           sys.stderr.write("Aieee! %s is unsupported format\n" % (options.install_upgrade))
       sys.exit(0)
       
except KeyboardInterrupt:
   sys.stderr.write("\nReceived immediate EXIT signal. Exiting!\n")
   sys.exit(1)