# -*- coding: utf-8 -*-

class SetterArgs():

    def __init__(self, filename, update, upgrade, install_packages, install_src_packages, \
                 src_build_dep, changelog, release, apt_backend, simulate=False):
        self.set = filename

        # self.set_update is of type boolean
        self.set_update = update

        # self.set_upgrade can be either True or False
        self.set_upgrade = upgrade
        self.upgrade_type = "upgrade"

        # Should be set to None for disabling or Tuple for activating
        self.set_install_packages = install_packages

        # To be implemented later
        self.src_build_dep = src_build_dep
        self.set_install_src_packages = install_src_packages
        self.set_install_release = release
        self.apt_backend = apt_backend
        self.set_simulate=simulate

        self.generate_changelog = changelog

    def __str__(self):
        print("self.set=",self.set)
        print("self.set_update=",self.set_update)
        print("self.set_upgrade=",self.set_upgrade)
        print("self.upgrade_type=",self.upgrade_type)
        print("self.set_install_packages=",self.set_install_packages)
        print("self.set_simulate=", self.set_simulate)

        return ""

class GetterArgs():

    def __init__(self, filename=None, bundle_file=None, socket_timeout=30, \
                    num_of_threads=1, disable_md5check=True, deb_bugs=False,
                        download_dir=None, cache_dir=None, proxy_host=None, proxy_port=None, progress_bar=None, progress_label=None):

        self.get = filename

        # TODO: to be implemented in next revision
        self.socket_timeout = socket_timeout
        self.num_of_threads = num_of_threads

        self.bundle_file = bundle_file
        self.disable_md5check = disable_md5check
        self.deb_bugs = deb_bugs
        self.download_dir = download_dir
        self.cache_dir = cache_dir

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        self.progress_bar = progress_bar
        self.progress_label = progress_label

    def __str__(self):
        print("self.get=",self.get)
        print("self.filename=",self.filename)
        print("self.bundle_file=",self.bundle_file)
        print("self.socket_timeout=",self.socket_timeout)
        print("self.num_of_threads=",self.num_of_threads)
        print("self.disable_md5_check=",self.disable_md5check)
        print("self.deb_bugs=",self.deb_bugs)
        print("self.download_dir=",self.download_dir)
        print("self.cache_dir=",self.cache_dir)

        return ""

'''
# install opts
        Str_InstallArg = args.install
        Bool_TestWindows = args.install_simulate
        Bool_SkipBugReports = args.skip_bug_reports
        Bool_Untrusted = args.allow_unauthenticated
        Str_InstallSrcPath = args.install_src_path
'''

class InstallerArgs():

    def __init__(self, filename=None, skip_bug_reports=True, skip_changelog=True, allow_unauthenticated=False, install_src_path=None, progress_bar=None, progress_label=None, simulate = False):

        self.install = filename

        # TODO: to be implemented in next revision
        self.install_simulate = simulate
        self.skip_bug_reports = skip_bug_reports
        self.skip_changelog = skip_changelog
        self.allow_unauthenticated = allow_unauthenticated
        self.install_src_path = install_src_path

        self.progress_bar = progress_bar
        self.progress_label = progress_label
