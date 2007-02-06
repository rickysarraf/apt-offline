import optparse

"""Contains most of the variables that are required by the application to run.
Also does command-line option parsing and variable validation."""

version = "0.6.4"
copyright = "(C) 2005 - 2007 Ritesh Raj Sarraf - RESEARCHUT (http://www.researchut.com/)"
        
errlist = []
supported_platforms = ["linux2", "gnu0", "gnukfreebsd5"]
apt_update_target_path = '/var/lib/apt/lists/'
apt_package_target_path = '/var/cache/apt/archives/'
# Dummy paths while testing on Windows
#apt_update_target_path = 'C:\\temp'
#apt_package_target_path = 'C:\\temp'
   
parser = optparse.OptionParser(usage="%prog [OPTION1, OPTION2, ...]", version="%prog " + version + "\n" + copyright)
   
parser.add_option("-d","--download-dir", dest="download_dir", help="Root directory path to save the downloaded files", action="store", type="string", metavar="pypt-downloads")
parser.add_option("-s","--cache-dir", dest="cache_dir", help="Root directory path where the pre-downloaded files will be searched. If not, give a period '.'",action="store", type="string", metavar=".")
parser.add_option("--verbose", dest="verbose", help="Enable verbose messages", action="store_true")
parser.add_option("--warnings", dest="warnings", help="Enable warnings", action="store_true")
parser.add_option("--debug", dest="debug", help="Enable Debug mode", action="store_true")
parser.add_option("-u","--uris", dest="uris_file", help="Full path of the uris file which contains the main database of files to be downloaded",action="store", type="string")
parser.add_option("","--disable-md5check", dest="disable_md5check", help="Disable md5checksum validation on downloaded files", action="store_true")
parser.add_option("", "--threads", dest="num_of_threads", help="Number of threads to spawn", action="store", type="int", metavar="1", default=1)
   
#INFO: Option zip is not enabled by default but is highly encouraged.
parser.add_option("-z","--zip", dest="zip_it", help="Zip the downloaded files to a single zip file", action="store_true")
parser.add_option("--zip-update-file", dest="zip_update_file", help="Default zip file for downloaded (update) data", action="store", type="string", metavar="pypt-offline-update.zip", default="pypt-offline-update.zip")
parser.add_option("--zip-upgrade-file", dest="zip_upgrade_file", help="Default zip file for downloaded (upgrade) data", action="store", type="string", metavar="pypt-offline-upgrade.zip", default="pypt-offline-upgrade.zip")
   
#INFO: At the moment nargs cannot be set to something like * so that optparse could manipulate n number of args. This is a limitation in optparse at the moment. The author might add this feature in the future.
# When fixed by the author, we'd be in a better shape to use the above mentioned line instead of relying on this improper way.
# With action="store_true", we are able to store all the arguments into the args variable from where it can be fetched later.
#parser.add_option("", "--set-install-packages", dest="set_install_packages", help="Extract the list of uris which need to be fetched for installation of the given package and its dependencies", action="store", type="string", nargs=10, metavar="package_name")
parser.add_option("", "--set-install", dest="set_install", help="Extract the list of uris which need to be fetched for installation of the given package and its dependencies", action="store", metavar="pypt-offline-install.dat")
parser.add_option("", "--set-install-packages", dest="set_install_packages", help="Name of the packages which need to be fetched", action="store_true", metavar="package_names")
   
parser.add_option("", "--set-update", dest="set_update", help="Extract the list of uris which need to be fetched for updation", action="store", type="string", metavar="pypt-offline-update.dat")
parser.add_option("", "--fetch-update", dest="fetch_update", help="Fetch the list of uris which are needed for apt's databases _updation_. This command must be executed on the WITHNET machine", action="store", type="string", metavar="pypt-offline-update.dat")
parser.add_option("", "--install-update", dest="install_update", help="Install the fetched database files to the  NONET machine and _update_ the apt database on the NONET machine. This command must be executed on the NONET machine", action="store", type="string", metavar="pypt-offline-update.zip")
parser.add_option("", "--set-upgrade", dest="set_upgrade", help="Extract the list of uris which need to be fetched for _upgradation_", action="store", type="string", metavar="pypt-offline-upgrade.dat")
parser.add_option("", "--upgrade-type", dest="upgrade_type", help="Type of upgrade to do. Use one of upgrade, dist-upgrade, dselect-ugprade", action="store", type="string", metavar="upgrade")
parser.add_option("", "--fetch-upgrade", dest="fetch_upgrade", help="Fetch the list of uris which are needed for apt's databases _upgradation_. This command must be executed on the WITHNET machine", action="store", type="string", metavar="pypt-offline-upgrade.dat")
parser.add_option("", "--install-upgrade", dest="install_upgrade", help="Install the fetched packages to the  NONET machine and _upgrade_ the packages on the NONET machine. This command must be executed on the NONET machine", action="store", type="string", metavar="pypt-offline-upgrade.zip")
(options, args) = parser.parse_args()