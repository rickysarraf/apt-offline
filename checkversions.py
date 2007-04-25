#
# checkversions.py - Find if the installed version of a package is the latest
#
#   Written by Chris Lawrence <lawrencc@debian.org>
#   (C) 2002-06 Chris Lawrence
#
# This program is freely distributable per the following license:
#
##  Permission to use, copy, modify, and distribute this software and its
##  documentation for any purpose and without fee is hereby granted,
##  provided that the above copyright notice appears in all copies and that
##  both that copyright notice and this permission notice appear in
##  supporting documentation.
##
##  I DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL
##  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL I
##  BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
##  DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
##  WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
##  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
##  SOFTWARE.
#
# $Id: checkversions.py,v 1.6.2.3 2006/10/16 18:52:41 lawrencc Exp $
#
# Version 3.35; see changelog for revision history

import sgmllib
#import HTMLParser

import os, re, sys, urllib2
from urlutils import open_url
from reportbug_exceptions import *

PACKAGES_URL = 'http://packages.debian.org/%s'
INCOMING_URL = 'http://incoming.debian.org/'
NEWQUEUE_URL = 'http://ftp-master.debian.org/new.html'

# The format is an unordered list

class BaseParser(sgmllib.SGMLParser):
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.savedata = None

    # --- Formatter interface, taking care of 'savedata' mode;
    # shouldn't need to be overridden

    def handle_data(self, data):
        if self.savedata is not None:
            self.savedata = self.savedata + data

    # --- Hooks to save data; shouldn't need to be overridden
    def save_bgn(self):
        self.savedata = ''

    def save_end(self, mode=0):
        data = self.savedata
        self.savedata = None
        if not mode and data is not None: data = ' '.join(data.split())
        return data

class PackagesParser(BaseParser):
    def __init__(self, arch='i386'):
        BaseParser.__init__(self)
        self.versions = {}
        self.row = None
        arch = r'\s(all|'+re.escape(arch)+r')\b'
        self.arch = re.compile(arch)
        self.dist = None

    def start_li(self, attrs):
        if self.row is not None:
            self.end_li()
        self.row = []

    def start_a(self, attrs):
        if self.row is not None:
            self.save_bgn()

    def end_a(self):
        if self.row is not None and self.savedata:
            self.dist = self.save_end()

    def lineend(self):
        line = self.save_end().strip()
        if self.arch.search(line):
            version = line.split(': ', 1)
            self.versions[self.dist] = version[0]

    def start_br(self, attrs):
        if self.savedata:
            self.lineend()
        self.save_bgn()

    def end_li(self):
        if self.savedata:
            self.lineend()
        self.row = None

class IncomingParser(sgmllib.SGMLParser):
    def __init__(self, package, arch='i386'):
        sgmllib.SGMLParser.__init__(self)
        self.found = []
        self.savedata = None
        arch = r'(?:all|'+re.escape(arch)+')'
        self.package = re.compile(re.escape(package)+r'_([^_]+)_'+arch+'.deb')

    def start_a(self, attrs):
        for attrib, value in attrs:
            if attrib.lower() != 'href':
                continue
            
            mob = self.package.match(value)
            if mob:
                self.found.append(mob.group(1))

class NewQueueParser(BaseParser):
    def __init__(self, package, arch='i386'):
        BaseParser.__init__(self)
        self.package = package
        self.row = None
        arch = r'\s(all|'+re.escape(arch)+r')\b'
        self.arch = re.compile(arch)
        self.versions = {}

    def start_tr (self, attrs):
        for name, value in attrs:
            if name == 'class' and value in ("odd", "even"):
                self.row = []

    def end_tr (self):
        if self.row is not None:
            # row (name, versions, architectures, distribution)
            dist = "%s (new queue)" % self.row[3]
            for version in self.row[1].split():
                self.versions[dist] = version
            self.row = None

    def start_td (self, attrs):
        if self.row is None:
            return
        self.save_bgn()

    def end_td (self):
        if self.row is None:
            return
        data = self.save_end()
        l = len(self.row)
        if l == 0:
            # package name
            if self.package == data:
                # found package name
                self.row.append(data)
            else:
                self.row = None
        elif l == 2:
            # architecture
            if self.arch.search(data):
                self.row.append(data)
            else:
                self.row = None
        else:
            self.row.append(data)

def compare_versions(current, upstream):
    """Return 1 if upstream is newer than current, -1 if current is
    newer than upstream, and 0 if the same."""
    if not upstream: return 0
    rc = os.system('dpkg --compare-versions %s lt %s' % (current, upstream))
    rc2 = os.system('dpkg --compare-versions %s gt %s' % (current, upstream))
    if not rc:
        return 1
    elif not rc2:
        return -1
    return 0

def later_version(a, b):
    if compare_versions(a, b) > 0:
        return b
    return a

def get_versions_available(package, dists=None, http_proxy=None, arch='i386'):
    if not dists:
        dists = ('stable', 'testing', 'unstable')

    try:
        page = open_url(PACKAGES_URL % package, http_proxy)
    except NoNetwork:
        return {}
    except urllib2.HTTPError, x:
        print >> sys.stderr, "Warning:", x
        return {}
    if not page:
        return {}

    parser = PackagesParser(arch)
    for line in page:
        parser.feed(line)
    parser.close()
    try:
        page.fp._sock.recv = None
    except:
        pass
    page.close()

##     content = page.read()
##     parser.feed(content)
##     parser.close()
##     page.close()

    versions = {}
    for dist in dists:
        if dist in parser.versions:
            versions[dist] = parser.versions[dist]
    del parser
    del page

    return versions

def get_newqueue_available(package, dists=None, http_proxy=None, arch='i386'):
    if dists is None:
        dists = ('unstable (new queue)', )
    try:
        page = open_url(NEWQUEUE_URL, http_proxy)
    except NoNetwork:
        return {}
    except urllib2.HTTPError, x:
        print >> sys.stderr, "Warning:", x
        return {}
    if not page:
        return {}
    parser = NewQueueParser(package, arch)
    for line in page:
        parser.feed(line)
    parser.close()
    try:
        page.fp._sock.recv = None
    except:
        pass
    page.close()

    #print repr(page)

    versions = {}
    for dist in dists:
        if dist in parser.versions:
            versions[dist] = parser.versions[dist]

    del parser
    del page
    #print 'HERE', gc.garbage
    return versions

def get_incoming_version(package, http_proxy=None, arch='i386'):
    try:
        page = open_url(INCOMING_URL, http_proxy)
    except NoNetwork:
        return None
    except urllib2.HTTPError, x:
        print >> sys.stderr, "Warning:", x
        return None
    if not page:
        return None
    
    parser = IncomingParser(package, arch)
    for line in page:
        parser.feed(line)
    parser.close()
    try:
        page.fp._sock.recv = None
    except:
        pass
    page.close()

    if parser.found:
        found = parser.found
        del parser
        return reduce(later_version, found, '0')

    del page
    del parser
    return None

import gc
def check_available(package, version, dists=None, check_incoming=True,
                    check_newqueue=True,
                    http_proxy=None, arch='i386'):
    avail = {}

    if check_incoming:
        iv = get_incoming_version(package, http_proxy, arch)
        if iv:
            avail['incoming'] = iv
    stuff = get_versions_available(package, dists, http_proxy, arch)
    avail.update(stuff)
    if check_newqueue:
        import reportbug
        srcpackage = reportbug.get_source_name(package)
	if srcpackage is None:
	    srcpackage = package
        stuff = get_newqueue_available(srcpackage, dists, http_proxy, arch)
        avail.update(stuff)
        #print gc.garbage, stuff

    new = {}
    newer = 0
    for dist in avail:
        if dist == 'incoming':
            if ':' in version:
                ver = version.split(':', 1)[1]
            else:
                ver = version
            comparison = compare_versions(ver, avail[dist])
        else:
            comparison = compare_versions(version, avail[dist])
        if comparison > 0:
            new[dist] = avail[dist]
        elif comparison < 0:
            newer += 1
    too_new = (newer and newer == len(avail))
    return new, too_new

if __name__=='__main__':
    import time
    import gc

    gc.set_debug(gc.DEBUG_LEAK)
    print get_newqueue_available('reportbug')
    print gc.garbage
    print check_available('reportbug', '3.7', arch='s390')
    #print check_available('openssh-server', '1:4.2p1-8', arch='i386')
    #print check_available('openssh-server', '1:4.2p1-8', arch='kfreebsd-i386')
    time.sleep(1000)
    #print check_available('dpkg', '1.10.2', arch='sparc')
