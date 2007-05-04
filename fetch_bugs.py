from pypt_core import FetchBugReportsDebian

package = raw_input("Please enter the Debian package name: ")
file = raw_input("Please enter the filename with full path: ")


if FetchBugReportsDebian(package, file) is True:
    print "Wrote bug report details for package %s to file %s.\n" % (package, file)