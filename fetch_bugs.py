#!/usr/bin/env python

import pypt_core

package = raw_input("Please enter the Debian package name: ")
package = package.rstrip("\r")
file = raw_input("Please enter the filename with full path: ")
file = file.rstrip("\r")

bugTypes = ["Resolved bugs", "Normal bugs", "Minor bugs", "Wishlist items", "FIXED"]


#if pypt_core.FetchBugReportsDebian(package, file) is True:
#    print "Wrote bug report details for package %s to file %s.\n" % (package, file)

BugReportDebian = pypt_core.FetchBugReports(file, bugTypes)

if BugReportDebian.FetchBugsDebian(package, file) is True:
    print "Wrote bug report details for package %s to file %s.\n" % (package, file)
else:
    print "No bugs found for package %s.\n" % (package)
