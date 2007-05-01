from pypt_core import FetchBugReportsDebian

package = "bash"
file = "/tmp/bug_report.txt"


if FetchBugReportsDebian(package, file) is True:
    print "Wrote bug report details for package %s to file %s.\n" % (package, file)