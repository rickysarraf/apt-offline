class SetterArgs():
    
    def __init__(self, filename, update, upgrade, install_packages):
        self.set = filename
        
        # self.set_update is of type boolean
        self.set_update = update
        
        # self.set_upgrad can be either True or False
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
    
