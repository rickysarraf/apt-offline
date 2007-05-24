#!/usr/bin/env python

import pypt_core

package = raw_input("Please enter the Debian package name: ")
file = raw_input("Please enter the filename with full path: ")


#if pypt_core.FetchBugReportsDebian(package, file) is True:
#    print "Wrote bug report details for package %s to file %s.\n" % (package, file)

BugReportDebian = pypt_core.FetchBugReports()

if BugReportDebian.FetchBugsDebian(package, file) is True:
    print "Wrote bug report details for package %s to file %s.\n" % (package, file)
else:
    print "No bugs found for package %s.\n" % (package)
