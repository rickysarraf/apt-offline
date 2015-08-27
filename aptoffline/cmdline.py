import argparse
import logging
from .util import releases
from .logger import initialize_logger


version = '1.8-dev'
copyright = '(c) 2005-2015 Ritesh Raj Sarraf'
license = 'This program comes with ABSOLUTELY NO WARRANTY\n'
'This is free software, and you are welcome to redistribute it under\n'
'the GNU GPL Version 3 (or later) license\n'
log = None


def _setter(args):
    pass


def _getter(parser):
    pass


def _installer(parser):
    pass


def _setup_parser(parser, method=None, func=None):
    parser.set_defaults(func=func)

    if method == 'set':
        # Write options for set subcommand here
        parser.add_argument('sig',
                            help=('Generate signature file'
                                  ' for specified operation'),
                            action='store', type=str,
                            metavar='apt-offline.sig',
                            default='apt-offline.sig')

        parser.add_argument('--install-packages', nargs='+',
                            help='Packages to be installed',
                            action='store', type=str, metavar='PKG')
        parser.add_argument('--update', action='store_true',
                            help=('Generate signature to '
                                  'update APT database'))
        parser.add_argument('--release', action='store',
                            metavar='release_name', choices=releases,
                            type=str,
                            help=('Distribution release from which'
                                  ' packages are to be installed.'))

        source = parser.add_argument_group('Source operations')
        source.add_argument('--install-src-packages', nargs='+',
                            help=('Source packages that need to'
                                  'be installed'),
                            action='store', type=str,
                            metavar='SRCPKG')
        parser.add_argument('--src-build-dep', action='store_true',
                            help=('Install Build dependency for'
                                  'requested source packages'))

        upgrade = parser.add_argument_group('Upgrade Operations')
        upgrade.add_argument('--upgrade', action='store_true',
                             help=('Generate signature to upgrade of'
                                   ' system'))
        upgrade.add_argument('--upgrade-type', action='store',
                             choices=['dist-upgrade', 'dselect-upgrade'],
                             help='Type of upgrade to do', type=str,
                             default='upgrade')
    elif method == 'get':
        # Write options for get subcommands here
        pass
    else:
        # write options for install subcommands here
        pass


def main():
    # Options which can be accessed even via sub-commands
    goptions = argparse.ArgumentParser(add_help=False)
    goptions.add_argument('-V', '--verbose',
                          help='enable verbose messages',
                          action='store_true')
    goptions.add_argument('-s', '--simulate',
                          help='Just simulate the operation',
                          action='store_true')

    # Actual parser, add paraents as goptions to access the above
    # options
    parser = argparse.ArgumentParser(
        description='offline APT package manager',
        epilog=copyright + ' - ' + license,
        parents=[goptions])
    parser.add_argument('-v', '--version', action='version', version=version)
    subcommands = parser.add_subparsers()

    set_parser = subcommands.add_parser('set', parents=[goptions])
    _setup_parser(set_parser, method='set', func=_setter)

    get_parser = subcommands.add_parser('get', parents=[goptions])
    _setup_parser(get_parser, method='get', func=_getter)

    install_parser = subcommands.add_parser('install', parents=[goptions])
    _setup_parser(install_parser, method='install', func=_installer)

    args = parser.parse_args()
    print(args)
    initialize_logger(args.verbose)
    global log
    log = logging.getLogger('apt-offline')
    try:
        args.func(args)
    except KeyboardInterrupt:
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
