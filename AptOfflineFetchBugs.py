#!/usr/bin/env python

'''
    pypt-offline  -- An offline package manager for Debian and its derivatives
    Copyright (C) 2007  Ritesh Raj Sarraf

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


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
