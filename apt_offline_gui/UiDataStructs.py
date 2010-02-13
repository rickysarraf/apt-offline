# -*- coding: utf-8 -*-
class SetterArgs():
    
    def __init__(self, filename, update, upgrade, install_packages):
        self.set = filename
        
        # self.set_update is of type boolean
        self.set_update = update
        
        # self.set_upgrade can be either True or False
        self.set_upgrade = upgrade
        self.upgrade_type = "upgrade"
        
        # Should be set to None for disabling or Tuple for activating
        self.set_install_packages = install_packages
        
        # To be implmented later
        self.src_build_dep = False
        self.set_install_src_packages = None
        self.set_install_release = False
    
    def __str__(self):
        print "self.set=",self.set
        print "self.set_update=",self.set_update
        print "self.set_upgrade=",self.set_upgrade
        print "self.upgrade_type=",self.upgrade_type
        print "self.set_install_packages=",self.set_install_packages
        
        return ""
    
class GetterArgs():

    def __init__(self, filename=None, bundle_file=None, socket_timeout=30, \
                    num_of_threads=1, disable_md5_check=True, deb_bugs=False,
                        download_dir=None, cache_dir=None):

        self.get = filename

        # TODO: to be implemented in next revision
        self.socket_timeout = socket_timeout
        self.num_of_threads = num_of_threads

        self.bundle_file = bundle_file
        self.disable_md5_check = disable_md5_check
        self.deb_bugs = deb_bugs
        self.download_dir = download_dir
        self.cache_dir = cache_dir


    def __str__(self):
        print "self.get=",self.get
        print "self.filename=",self.filename
        print "self.bundle_file=",self.bundle_file
        print "self.socket_timeout=",self.socket_timeout
        print "self.num_of_threads=",self.num_of_threads
        print "self.disable_md5_check=",self.disable_md5_check
        print "self.deb_bugs=",self.deb_bugs
        print "self.download_dir=",self.download_dir
        print "self.cache_dir=",self.cache_dir
        
        return ""

