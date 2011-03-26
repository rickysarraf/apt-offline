#
# debianbts.py - Routines to deal with the debbugs web pages
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
#
# $Id: debianbts.py,v 1.24.2.7 2006/10/16 17:14:03 lawrencc Exp $

import sgmllib, glob, os, re, rfc822, time, urllib
from AptOffline_urlutils import open_url
from AptOffline_reportbug_exceptions import NoNetwork
import sys

import mailbox
import email
import email.Errors
import cStringIO
import cgi

def msgfactory(fp):
    try:
        return email.message_from_file(fp)
    except email.Errors.MessageParseError:
        # Don't return None since that will
        # stop the mailbox iterator
        return ''
    
class Error(Exception):
    pass

# Severity levels
SEVERITIES = {
    'critical' : """makes unrelated software on the system (or the
    whole system) break, or causes serious data loss, or introduces a
    security hole on systems where you install the package.""",
    'grave' : """makes the package in question unusable by most or all users,
    or causes data loss, or introduces a security hole allowing access 
    to the accounts of users who use the package.""",
    'serious' : """is a severe violation of Debian policy (that is,
    the problem is a violation of a 'must' or 'required' directive);
    may or may not affect the usability of the package.  Note that non-severe
    policy violations may be 'normal,' 'minor,' or 'wishlist' bugs.
    (Package maintainers may also designate other bugs as 'serious' and thus
    release-critical; however, end users should not do so.)""",
    'important' : """a bug which has a major effect on the usability
    of a package, without rendering it completely unusable to
    everyone.""",
    'does-not-build' : """a bug that stops the package from being built
    from source.  (This is a 'virtual severity'.)""",
    'normal' : """a bug that does not undermine the usability of the
    whole package; for example, a problem with a particular option or
    menu item.""",
    'minor' : """things like spelling mistakes and other minor
    cosmetic errors that do not affect the core functionality of the
    package.""",
    'wishlist' : "suggestions and requests for new features.",
    }

# justifications for critical bugs
JUSTIFICATIONS = {
    'critical' : (
    ('breaks unrelated software', """breaks unrelated software on the system
    (packages that have a dependency relationship are not unrelated)"""),
    ('breaks the whole system', """renders the entire system unusable (e.g.,
    unbootable, unable to reach a multiuser runlevel, etc.)"""),
    ('causes serious data loss', """causes loss of important, irreplaceable
    data"""),
    ('root security hole', """introduces a security hole allowing access to
    root (or another privileged system account), or data normally
    accessible only by such accounts"""),
    ('unknown', """not sure, or none of the above"""),
    ),
    'grave' : (
    ('renders package unusable', """renders the package unusable, or mostly
    so, on all or nearly all possible systems on which it could be installed
    (i.e., not a hardware-specific bug); or renders package uninstallable
    or unremovable without special effort"""),
    ('causes non-serious data loss', """causes the loss of data on the system
    that is unimportant, or restorable without resorting to backup media"""),
    ('user security hole', """introduces a security hole allowing access to
    user accounts or data not normally accessible"""),
    ('unknown', """not sure, or none of the above"""),
    )
    }


# Ordering for justifications
JUSTORDER = {
    'critical' :  ['breaks unrelated software',
                   'breaks the whole system',
                   'causes serious data loss',
                   'root security hole',
                   'unknown'],
    'grave' : ['renders package unusable',
               'causes non-serious data loss',
               'user security hole',
               'unknown']
    }

SEVERITIES_gnats = {
    'critical' : 'The product, component or concept is completely'
    'non-operational or some essential functionality is missing.  No'
    'workaround is known.',
    'serious' : 'The product, component or concept is not working'
    'properly or significant functionality is missing.  Problems that'
    'would otherwise be considered ''critical'' are rated ''serious'' when'
    'a workaround is known.',
    'non-critical' : 'The product, component or concept is working'
    'in general, but lacks features, has irritating behavior, does'
    'something wrong, or doesn''t match its documentation.',
    }

# Rank order of severities, for sorting
SEVLIST = ['critical', 'grave', 'serious', 'important', 'does-not-build',
           'normal', 'non-critical', 'minor', 'wishlist', 'fixed']

def convert_severity(severity, type='debbugs'):
    "Convert severity names if needed."
    if type == 'debbugs':
        return {'non-critical' : 'normal'}.get(severity, severity)
    elif type == 'gnats':
        return {'grave' : 'critical',
                'important' : 'serious',
                'normal' : 'non-critical',
                'minor' : 'non-critical',
                'wishlist' : 'non-critical'}.get(severity, severity)
    else:
        return severity

# These packages are virtual in Debian; we don't look them up...
debother = {
    'base' : 'General bugs in the base system',
# Actually a real package, but most people don't have boot-floppies installed for good reason
#    'boot-floppy' : '(Obsolete, please use boot-floppies instead.)',
    'boot-floppies' : 'Bugs in the woody installation subsystem',
    'bugs.debian.org' : 'The bug tracking system, @bugs.debian.org',
    'cdimage.debian.org' : 'CD Image issues',
    'cdrom' : 'Problems with installation from CD-ROMs',
# dpkg-iwj -- The dpkg branch maintained by Ian Jackson
    'debian-policy' : 'Proposed changes in the Debian policy documentation',
    'ftp.debian.org' : 'Problems with the FTP site',
    'general' : 'General problems (e.g., that many manpages are mode 755)',
    'install' : 'Problems with the sarge installer.',
    'installation' : 'General installation problems not covered otherwise.',
#    'kernel' : '(Obsolete, please use "linux-image" instead.)',
    'linux-image' : 'Problems with the Linux kernel, or the kernel shipped with Debian',
    'listarchives' :  'Problems with the WWW mailing list archives',
    'lists.debian.org' : 'The mailing lists, debian-*@lists.debian.org.',
    'mirrors' : 'Problems with Debian archive mirrors.',
    'nonus.debian.org' : 'Problems with the non-US FTP site',
    'press' : 'Press release issues',
    'project' : 'Problems related to Project administration',
    'qa.debian.org' : 'Problems related to the quality assurance group',
#slink-cd -- Slink CD 
#spam -- Spam (reassign spam to here so we can complain about it)
    'security.debian.org' : 'Problems with the security updates server',
    'upgrade-reports' : 'Reports of successful and unsucessful upgrades',
    'wnpp' : 'Work-Needing and Prospective Packages list',
    'www.debian.org' : 'Problems with the WWW site (including other *.debian.org sites)'
    }

progenyother = {
    'debian-general' : 'Any non-package-specific bug',
    }

def handle_wnpp(package, bts, ui, fromaddr, online=True, http_proxy=None):
    desc = body = ''
    headers = []
    pseudos = []
    query = True
    
    tag = ui.menu('What sort of request is this?  (If none of these '
                  'things mean anything to you, or you are trying to report '
                  'a bug in an existing package, please press Enter to '
                  'exit reportbug.)', {
        'O' :
        "The package has been `Orphaned'. It needs a new maintainer as soon as possible.",
        'RFA' :
        "This is a `Request for Adoption'. Due to lack of time, resources, interest or something similar, the current maintainer is asking for someone else to maintain this package. He/she will maintain it in the meantime, but perhaps not in the best possible way. In short: the package needs a new maintainer.",
        'RFH' :
        "This is a `Request For Help'. The current maintainer wants to continue to maintain this package, but he/she needs some help to do this, because his/her time is limited or the package is quite big and needs several maintainers.",
        'ITP' :
        "This is an `Intent To Package'. Please submit a package description along with copyright and URL in such a report.",
        'RFP' :
        "This is a `Request For Package'. You have found an interesting piece of software and would like someone else to maintain it for Debian. Please submit a package description along with copyright and URL in such a report.",
        }, 'Choose the request type: ', empty_ok=True)
    if not tag:
        ui.long_message('To report a bug in a package, use the name of the package, not wnpp.\n')
        raise SystemExit

    if tag in ('RFP', 'ITP'):
        prompt = 'Please enter the proposed package name: '
    else:
        prompt = 'Please enter the name of the package: '
    package = ui.get_string(prompt)
    if not package: return

    ui.ewrite('Checking status database...\n')
    info = reportbug.get_package_status(package)
    available = info[1]

    severity = 'normal'
    if tag in ('ITP', 'RFP'):
        if available and (not online or checkversions.check_available(
            package, '0', http_proxy=http_proxy)):
            if not ui.yes_no(
                ('A package called %s already appears to exist (at least on '
                 'your system); continue?' % package),
                'Ignore this problem and continue.  If you have '
                'already locally created a package with this name, this '
                'warning message may have been produced in error.',
                'Exit without filing a report.', default=0):
                sys.exit(1)
            
        severity = 'wishlist'

        desc = ui.get_string(
            'Please briefly describe this package; this should be an '
            'appropriate short description for the eventual package: ')
        if not desc:
            return

        if tag == 'ITP':
            headers.append('X-Debbugs-CC: debian-devel@lists.debian.org')
            pseudos.append('Owner: %s' % fromaddr)
            ui.ewrite('Your report will be carbon-copied to debian-devel, '
                      'per Debian policy.\n')

        body = """* Package name    : %s
  Version         : x.y.z
  Upstream Author : Name <somebody@example.org>
* URL             : http://www.example.org/
* License         : (GPL, LGPL, BSD, MIT/X, etc.)
  Programming Lang: (C, C++, C#, Perl, Python, etc.)
  Description     : %s

(Include the long description here.)
""" % (package, desc)
    elif tag in ('O', 'RFA', 'RFH'):
        severity = 'normal'
        query = False
        if not available:
            info = reportbug.get_source_package(package)
            if info:
                info = reportbug.get_package_status(info[0][0])

        if not info:
            cont = ui.select_options(
                "This package doesn't appear to exist; continue?",
                'yN', {'y': 'Ignore this problem and continue.',
                       'n': 'Exit without filing a report.' })
            if cont == 'n':
                sys.exit(1)
            desc = fulldesc = ''
        else:
            desc = info[11] or ''
            package = info[12] or package
            fulldesc = info[13]

        if tag == 'O' and info and info[9] in \
               ('required', 'important', 'standard'):
            severity = 'important'

        if tag == 'RFH':
            headers.append('X-Debbugs-CC: debian-devel@lists.debian.org')
            ui.ewrite('Your request will be carbon-copied to debian-devel, '
                      'per Debian policy.\n')

        if fulldesc:
            orphstr = 'intend to orphan'
            if tag == 'RFA':
                orphstr = 'request an adopter for'
            elif tag == 'RFH':
                orphstr = 'request assistance with maintaining'
                
            body = ('I %s the %s package.\n\n'
                    'The package description is:\n') % (orphstr, package)
            body = body + fulldesc + '\n'
        
    if desc:
        subject = '%s: %s -- %s' % (tag, package, desc)
    else:
        subject = '%s: %s' % (tag, package)

    return (subject, severity, headers, pseudos, body, query)

# Supported servers
# Theoretically support for GNATS and Jitterbug could be added here.
SYSTEMS = { 'debian' :
            { 'name' : 'Debian', 'email': '%s@bugs.debian.org',
              'btsroot' : 'http://www.debian.org/Bugs/',
              'otherpkgs' : debother,
              'nonvirtual' : ['linux-image', 'kernel-image'],
              'specials' : { 'wnpp': handle_wnpp },
              # Dependency packages
              'deppkgs' : ('gcc', 'g++', 'cpp', 'gcj', 'gpc', 'gobjc',
                           'chill', 'gij', 'g77', 'python', 'python-base',
                           'x-window-system-core', 'x-window-system'),
              'cgiroot' : 'http://bugs.debian.org/cgi-bin/' },
            'kde' :
            { 'name' : 'KDE Project', 'email': '%s@bugs.kde.org',
              'btsroot': 'http://bugs.kde.org/' },
            'mandrake' :
            { 'name' : 'Linux-Mandrake', 'email': '%s@bugs.linux-mandrake.com',
              'type' : 'mailto', 'query-dpkg' : False },
            'gnome' :
            { 'name' : 'GNOME Project', 'email': '%s@bugs.gnome.org',
              'type' : 'mailto', 'query-dpkg' : False },
            'ximian' :
            { 'name' : 'Ximian', 'email': '%s@bugs.ximian.com',
              'type' : 'mailto' },
            'progeny' :
            { 'name' : 'Progeny', 'email' : 'bugs@progeny.com',
              'type' : 'gnats', 'otherpkgs' : progenyother },
            'ubuntu' :
            { 'name' : 'Ubuntu', 'email' : 'ubuntu-users@lists.ubuntu.com',
              'type' : 'mailto' },
            'guug' :
            { 'name' : 'GUUG (German Unix User Group)',
              'email' : '%s@bugs.guug.de', 'query-dpkg' : False },
            'grml' :
            { 'name' : 'grml', 'email': '%s@bugs.grml.org',
              'btsroot' : 'http://bugs.grml.org/',
              'cgiroot' : 'http://bugs.grml.org/cgi-bin/' },
            }

SYSTEMS['helixcode'] = SYSTEMS['ximian']

CLASSES = {
    'sw-bug' : 'The problem is a bug in the software or code.  For'
    'example, a crash would be a sw-bug.',
    'doc-bug' : 'The problem is in the documentation.  For example,'
    'an error in a man page would be a doc-bug.',
    'change-request' : 'You are requesting a new feature or a change'
    'in the behavior of software, or are making a suggestion.  For'
    'example, if you wanted reportbug to be able to get your local'
    'weather forecast, as well as report bugs, that would be a'
    'change-request.',
    }

CLASSLIST = ['sw-bug', 'doc-bug', 'change-request']

CRITICAL_TAGS = {
    'security' : 'This problem is a security vulnerability in Debian.',
}

TAGS = {
    'patch' : 'You are including a patch to fix this problem.',
##    'upstream' : 'You believe this problem is not specific to Debian.',
##    'potato' : 'This bug only applies to the potato release (Debian 2.2).',
##    'woody' : 'This bug only applies to the woody release (Debian 3.0).',
##    'sarge' : 'This bug only applies to the sarge release (Debian 3.1).',
##    'sid' : 'This bug only applies to the unstable branch of Debian.',
    "l10n" : "This bug reports a localization/internationalization issue.",
##    'done' : 'No more tags.',
    }

EXTRA_TAGS = ['potato', 'woody', 'sarge', 'security', 'sid', 'upstream']

TAGLIST = ['l10n', 'patch']
CRITICAL_TAGLIST = ['security']

def yn_bool(setting):
    if setting:
        if str(setting) == 'no':
            return 'no'
        return 'yes'
    else:
        return 'no'

def cgi_report_url(system, number, archived=False, mbox=False):
    root = SYSTEMS[system].get('cgiroot')
    if root:
        return '%sbugreport.cgi?bug=%d&archived=%s&mbox=%s' % (
            root, number, archived, yn_bool(mbox))
    return None

def cgi_package_url(system, package, archived=False, source=False,
                    repeatmerged=True, version=None):
    root = SYSTEMS[system].get('cgiroot')
    if not root: return None
    
    #package = urllib.quote_plus(package.lower())
    if source:
        query = {'src' : package.lower()}
    else:
        query = {'pkg' : package.lower()}

    query['repeatmerged'] = yn_bool(repeatmerged)
    query['archived'] = yn_bool(archived)

    if version:
        query['version'] = str(version)
    
    qstr = urllib.urlencode(query)
    #print qstr
    return '%spkgreport.cgi?%s' % (root, qstr)

def package_url(system, package, mirrors=None, source=False,
                repeatmerged=True):
    btsroot=get_btsroot(system, mirrors)
    package = urllib.quote_plus(package.lower())
    return btsroot+('db/pa/l%s.html' % package) 

def report_url(system, number, mirrors=None):
    number = str(number)
    if len(number) < 2: return None
    btsroot=get_btsroot(system, mirrors)
    return btsroot+('db/%s/%s.html' % (number[:2], number))

def get_package_url(system, package, mirrors=None, source=False,
                    archived=False, repeatmerged=True):
    return (cgi_package_url(system, package, archived, source, repeatmerged) or
            package_url(system, package, mirrors, source, repeatmerged))

def get_report_url(system, number, mirrors=None, archived=False, mbox=False):
    return (cgi_report_url(system, number, archived, mbox) or
            report_url(system, number, mirrors))

def parse_bts_url(url):
    bits = url.split(':', 1)
    if len(bits) != 2: return None

    type, loc = bits
    if loc.startswith('//'): loc = loc[2:]
    while loc.endswith('/'): loc = loc[:-1]
    return type, loc

# Dynamically add any additional systems found
for origin in glob.glob('/etc/dpkg/origins/*'):
    try:
        fp = file(origin)
        system = os.path.basename(origin)
        SYSTEMS[system] = SYSTEMS.get(system, { 'otherpkgs' : {},
                                                'query-dpkg' : True,
                                                'mirrors' : {},
                                                'cgiroot' : None } )
        for line in fp:
            try:
                (header, content) = line.split(': ', 1)
                header = header.lower()
                content = content.strip()
                if header == 'vendor':
                    SYSTEMS[system]['name'] = content
                elif header == 'bugs':
                    (type, root) = parse_bts_url(content)
                    SYSTEMS[system]['type'] = type
                    if type == 'debbugs':
                        SYSTEMS[system]['btsroot'] = 'http://'+root+'/'
                        SYSTEMS[system]['email'] = '%s@'+root
                    elif type == 'mailto':
                        SYSTEMS[system]['btsroot'] = None
                        SYSTEMS[system]['email'] = root
                    else:
                        # We don't know what to do...
                        pass
            except ValueError:
                pass
        fp.close()
    except IOError:
        pass

# For summary pages, we want to keep:
#
# - Contents of <title>...</title>
# - Contents of <h2>...</h2>
# - Contents of each <li>
#
# For individual bugs, we want to keep:
# - Contents of <title>...</title>
# - Contents of every <pre>...</pre> after a <h2>....</h2> tag.

class BTSParser(sgmllib.SGMLParser):
    def __init__(self, mode='summary', cgi=False, followups=False):
        sgmllib.SGMLParser.__init__(self)
        self.hierarchy = []
        self.lidata = None
        self.lidatalist = None
        self.savedata = None
        self.title = None
        self.bugcount = 0
        self.mode = mode
        self.cgi = cgi
        self.followups = followups
        self.inbuglist = self.intrailerinfo = False
        self.bugtitle = None
        if followups:
            self.preblock = []
        else:
            self.preblock = ''
        self.endh2 = False

    # --- Formatter interface, taking care of 'savedata' mode;
    # shouldn't need to be overridden

    def handle_data(self, data):
        if self.savedata is not None:
            self.savedata += data

    # --- Hooks to save data; shouldn't need to be overridden

    def save_bgn(self):
        self.savedata = ''

    def save_end(self, mode=False):
        data = self.savedata
        if not mode and data:
            data = ' '.join(data.split())
        self.savedata = None
        return data

    def start_h1(self, attrs):
        self.save_bgn()
        self.oldmode = self.mode
        self.mode = 'title'

    def end_h1(self):
        self.title = self.save_end()
        self.mode = self.oldmode

    def start_h2(self, attrs):
        if self.lidata: self.check_li()

        self.save_bgn()

    def end_h2(self):
        if self.mode == 'summary':
            hiertitle = self.save_end()
            if 'bug' in hiertitle:
                self.hierarchy.append( (hiertitle, []) )
        self.endh2 = True # We are at the end of a title, flag <pre>

    def start_ul(self, attrs):
        if self.mode == 'summary':
            for k, v in attrs:
                if k == 'class' and v == 'bugs':
                    self.inbuglist = True

    def end_ul(self):
        if self.inbuglist:
            self.check_li()
        
        self.inbuglist = False

    def do_br(self, attrs):
        if self.mode == 'title':
            self.savedata = ""
        elif self.mode == 'summary' and self.inbuglist and not self.intrailerinfo:
            self.bugtitle = self.save_end()
            self.intrailerinfo = True
            self.save_bgn()

    def check_li(self):
        if self.mode == 'summary':
            if not self.intrailerinfo:
                self.bugtitle = self.save_end()
                trailinfo = ''
            else:
                trailinfo = self.save_end()

            match = re.search(r'fixed:\s+([\w.+~-]+(\s+[\w.+~:-]+)?)', trailinfo)
            if match:
                title = self.bugtitle
                bits = re.split(r':\s+', title, 1)
                if len(bits) > 1:
                    buginfo = '%s [FIXED %s]: %s' % (
                        bits[0], match.group(1), bits[1])
                else:
                    if title.endswith(':'):
                        title = title[:-1]
                    
                    buginfo = '%s [FIXED %s]' % (title, match.group(1))
            else:
                buginfo = self.bugtitle
            
            self.lidatalist.append(buginfo)
            self.bugcount += 1

            self.lidata = self.intrailerinfo = False

    def do_li(self, attrs):
        if self.mode == 'summary' and self.inbuglist:
            if self.lidata: self.check_li()

            self.lidata = True
            if self.hierarchy:
                self.lidatalist = self.hierarchy[-1][1]
            else:
                self.lidatalist = []
            self.save_bgn()

    def start_pre(self, attrs):
        "Save <pre> when we follow a </h2>"
        if self.followups:
            if not self.endh2: return
        else:
            if self.cgi and self.preblock: return
        
        self.save_bgn()

    def end_pre(self):
        if self.followups:
            if not self.endh2: return
            self.endh2 = False	# Done with a report, reset </h2>.
            stuff = self.save_end(1)
            if not self.cgi:
                self.preblock.insert(0, stuff)
            else:
                self.preblock.append(stuff)
        elif not (self.preblock and self.cgi):
            self.preblock = self.save_end(1)

    def reorganize(self):
        if not self.hierarchy:
            return

        newhierarchy = []
        fixed = []
        fixedfinder = re.compile(r'\[FIXED ([^\]]+)\]')
        resolvedfinder = re.compile(r'Resolved')

        for (title, buglist) in self.hierarchy:
            if 'Resolved' in title:
                newhierarchy.append( (title, buglist) )
                continue
            
            bugs = []
            for bug in buglist:
                if fixedfinder.search(bug):
                    fixed.append(bug)
                else:
                    bugs.append(bug)
                    
            if bugs:
                title = ' '.join(title.split()[:-2])
                if len(bugs) != 1:
                    title += ' (%d bugs)' % len(bugs)
                else:
                    title += ' (1 bug)'
                
                newhierarchy.append( (title, bugs) )

        if fixed:
            self.hierarchy = [('Bugs fixed in subsequent releases (%d bugs)' % len(fixed), fixed)] + newhierarchy

def parse_html_report(number, url, http_proxy, followups=False, cgi=True):
    page = open_url(url, http_proxy)
    if not page:
        return None

    parser = BTSParser(cgi=cgi, followups=followups)
    for line in page:
        parser.feed(line)
    parser.close()

    try:
        page.fp._sock.recv = None
    except:
        pass
    page.close()

    items = parser.preblock
    title = "#%d: %s" % (number, parser.title)

    if not followups:
        items = [items]

    output = []
    for stuff in items:
        parts = stuff.split('\n\n')
        match = re.search('^Date: (.*)$', parts[0], re.M | re.I)
        date_submitted = ''
        if match:
            date_submitted = 'Date: %s\n' % match.group(1)

        stuff = ('\n\n'.join(parts[1:])).rstrip()
        if not stuff:
            continue

        item = date_submitted+stuff+os.linesep
        output.append(item)

    if not output:
        return None

    return (title, output)

# XXX: Need to handle charsets properly
def parse_mbox_report(number, url, http_proxy, followups=False):
    page = open_url(url, http_proxy)
    if not page:
        return None

    # Make this seekable
    wholefile = cStringIO.StringIO(page.read())

    try:
        page.fp._sock.recv = None
    except:
        pass
    page.close()

    mbox = mailbox.UnixMailbox(wholefile, msgfactory)
    title = ''

    output = []
    for message in mbox:
        if not message:
            pass
        
        subject = message.get('Subject')
        if not title:
            title = subject

        date = message.get('Date')
        fromhdr = message.get('From')

        body = entry = ''
        for part in message.walk():
            if part.get_content_type() == 'text/plain' and not body:
                body = part.get_payload(None, True)

        if fromhdr:
            entry += 'From: %s%s' % (fromhdr, os.linesep)

        if subject and subject != title:
            entry += 'Subject: %s%s' % (subject, os.linesep)

        if date:
            entry += 'Date: %s%s' % (date, os.linesep)

        if entry:
            entry += os.linesep

        entry += body.rstrip('\n') + os.linesep

        output.append(entry)

    if not output:
        return None

    title = "#%d: %s" % (number, title)
    return (title, output)

def get_cgi_reports(package, system='debian', http_proxy='', archived=False,
                    source=False, version=None):
    try:
	    page = open_url(cgi_package_url(system, package, archived, source,
                                    version=version), http_proxy)
    except NoNetwork:
	    page = None
    if not page:
        return (0, None, None)

    #content = page.read()
    #if 'Maintainer' not in content:
    #    return (0, None, None)
    
    parser = BTSParser(cgi=True)
    for line in page:
        parser.feed(line)
    parser.close()
    try:
        page.fp._sock.recv = None
    except:
        pass
    page.close()

    # Reorganize hierarchy to put recently-fixed bugs at top
    parser.reorganize()

    data = (parser.bugcount, parser.title, parser.hierarchy)
    del parser

    return data

def get_cgi_report(number, system='debian', http_proxy='', archived=False,
                   followups=False):
    number = int(number)

    url = cgi_report_url(system, number, archived='no', mbox=True)
    return parse_mbox_report(number, url, http_proxy, followups)
    #return parse_html_report(number, url, http_proxy, followups, cgi=True)

def get_btsroot(system, mirrors=None):
    if mirrors:
        alternates = SYSTEMS[system].get('mirrors')
        for mirror in mirrors:
            if alternates.has_key(mirror):
                return alternates[mirror]
    return SYSTEMS[system].get('btsroot', '')

def get_reports(package, system='debian', mirrors=None, version=None,
                http_proxy='', archived=False, source=False):
    if isinstance(package, basestring):
        if SYSTEMS[system].get('cgiroot'):
            result = get_cgi_reports(package, system, http_proxy, archived,
                                     source, version=version)
            if result: return result

        url = package_url(system, package, mirrors, source)
        page = open_url(url, http_proxy)
        if not page:
            return (0, None, None)

        #content = page.read()
        #if 'Maintainer' not in content:
        #    return (0, None, None)

        parser = BTSParser()
        for line in page:
            parser.feed(line)
        parser.close()
        try:
            page.fp._sock.recv = None
        except:
            pass
        page.close()

        return parser.bugcount, parser.title, parser.hierarchy

    # A list of bug numbers
    this_hierarchy = []
    package = [int(x) for x in package]
    package.sort()
    for bug in package:
        result = get_report(bug, system, mirrors, http_proxy, archived)
        if result:
            title, body = result
            this_hierarchy.append(title)
            #print title
    
    title = "Multiple bug reports"
    bugcount = len(this_hierarchy)
    hierarchy = [('Reports', this_hierarchy)]

    return bugcount, title, hierarchy

def get_report(number, system='debian', mirrors=None,
               http_proxy='', archived=False, followups=False):

    try:
            number = int(number)
    except ValueError:
            sys.stderr.write("%s couldn't be convered to integer.\nPlease report a bug" % (number) )
            return False
    if SYSTEMS[system].get('cgiroot'):
        result = get_cgi_report(number, system, http_proxy, archived,
                                followups)
        if result: return result
        
    url = report_url(system, number, mirrors)
    if not url: return None

    return parse_html_report(number, url, http_proxy, followups, cgi=False)

class NullParser(sgmllib.SGMLParser):
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)

if __name__ == '__main__':
    import pprint

    data = get_cgi_reports('reportbug')
    pprint.pprint(data)
    time.sleep(1000)
