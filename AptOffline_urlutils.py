#
# urlutils.py - Simplified urllib handling
#
#   Written by Chris Lawrence <lawrencc@debian.org>
#   (C) 1999-2006 Chris Lawrence
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
# Version 3.35; see changelog for revision history

import httplib
import urllib
import urllib2
import getpass
import re
import socket
import commands
import os
import sys
from AptOffline_reportbug_exceptions import *
try:
    import webbrowser
except:
    webbrowser = None

UA_STR = 'reportbug/3.35 (Debian)'

def decode (page):
    "gunzip or deflate a compressed page"
    #print page.info().headers
    encoding = page.info().get("Content-Encoding") 
    if encoding in ('gzip', 'x-gzip', 'deflate'):
        from cStringIO import StringIO
        # cannot seek in socket descriptors, so must get content now
        content = page.read()
        if encoding == 'deflate':
            import zlib
            fp = StringIO(zlib.decompress(content))
        else:
            import gzip
            fp = gzip.GzipFile('', 'rb', 9, StringIO(content))
        # remove content-encoding header
        headers = httplib.HTTPMessage(StringIO(""))
        ceheader = re.compile(r"(?i)content-encoding:")
        for h in page.info().keys():
            if not ceheader.match(h):
                headers[h] = page.info()[h]
        newpage = urllib.addinfourl(fp, headers, page.geturl())
        # Propagate code, msg through
        if hasattr(page, 'code'):
            newpage.code = page.code
        if hasattr(page, 'msg'):
            newpage.msg = page.msg
        return newpage
    return page

class HttpWithGzipHandler (urllib2.HTTPHandler):
    "support gzip encoding"
    def http_open (self, req):
        return decode(urllib2.HTTPHandler.http_open(self, req))

if hasattr(httplib, 'HTTPS'):
    class HttpsWithGzipHandler (urllib2.HTTPSHandler):
        "support gzip encoding"
        def http_open (self, req):
            return decode(urllib2.HTTPSHandler.http_open(self, req))

class handlepasswd(urllib2.HTTPPasswordMgrWithDefaultRealm):
    def find_user_password(self, realm, authurl):
        user, password = urllib2.HTTPPasswordMgrWithDefaultRealm.find_user_password(self, realm, authurl)
        if user is not None:
            return user, password

        user = raw_input('Enter username for %s at %s: ' % (realm, authurl))
        password = getpass.getpass(
            "Enter password for %s in %s at %s: " % (user, realm, authurl))
        self.add_password(realm, authurl, user, password)
        return user, password
        
_opener = None
def urlopen(url, proxies=None, data=None):
    global _opener

    if not proxies:
        proxies = urllib.getproxies()

    headers = {'User-Agent': UA_STR,
               'Accept-Encoding' : 'gzip;q=1.0, deflate;q=0.9, identity;q=0.5'}
    
    req = urllib2.Request(url, data, headers)

    proxy_support = urllib2.ProxyHandler(proxies)
    if _opener is None:
        pwd_manager = handlepasswd()
        handlers = [proxy_support,
            urllib2.UnknownHandler, HttpWithGzipHandler,
            urllib2.HTTPBasicAuthHandler(pwd_manager),
            urllib2.ProxyBasicAuthHandler(pwd_manager),
            urllib2.HTTPDigestAuthHandler(pwd_manager),
            urllib2.ProxyDigestAuthHandler(pwd_manager),
            urllib2.HTTPDefaultErrorHandler, urllib2.HTTPRedirectHandler,
        ]
        if hasattr(httplib, 'HTTPS'):
            handlers.append(HttpsWithGzipHandler)
        _opener = urllib2.build_opener(*handlers)
        # print _opener.handlers
        urllib2.install_opener(_opener)
    
    return _opener.open(req)

# Global useful URL opener; returns None if the page is absent, otherwise
# like urlopen
def open_url(url, http_proxy=None):
    proxies = urllib.getproxies()
    if http_proxy:
        proxies['http'] = http_proxy

    try:
        page = urlopen(url, proxies)
    except urllib2.HTTPError, x:
        if x.code in (404, 500, 503):
            return None
        else:
            raise
    except (socket.gaierror, socket.error, urllib2.URLError), x:
        raise NoNetwork
    except IOError, data:
        if data and data[0] == 'http error' and data[1] == 404:
            return None
        else:
            raise NoNetwork
    except TypeError:
        print >> sys.stderr, "http_proxy environment variable must be formatted as a valid URI"
        raise NoNetwork
    return page

def launch_browser(url):
    if not os.system('command -v sensible-browser &> /dev/null'):
        cmd = 'sensible-browser' + commands.mkarg(url)
        os.system(cmd)
        return
    
    if webbrowser:
        webbrowser.open(url)
        return

    X11BROWSER = os.environ.get('X11BROWSER', 'mozilla-firefox')
    CONSOLEBROWSER = os.environ.get('CONSOLEBROWSER', 'lynx')

    if (os.environ.has_key('DISPLAY') and
        not os.system('command -v '+X11BROWSER+' &> /dev/null')):
        cmd = "%s %s &" % (X11BROWSER, commands.mkarg(url))
    else:
        cmd = "%s %s" % (CONSOLEBROWSER, commands.mkarg(url))

    os.system(cmd)

if __name__ == '__main__':
    page = open_url('http://bugs.debian.org/reportbug')
    content = page.read()
    print page.info().headers
