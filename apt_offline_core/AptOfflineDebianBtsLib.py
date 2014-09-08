#!/usr/bin/env python

# debianbts.py - Methods to query Debian's BTS.
# Copyright (C) 2007-2010  Bastian Venthur <venthur@debian.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


"""Query Debian's Bug Tracking System (BTS).

This module provides a layer between Python and Debian's BTS. It provides
methods to query the BTS using the BTS' SOAP interface, and the Bugreport class
which represents a bugreport from the BTS.
"""


from datetime import datetime
import urllib
import urlparse

import SOAPpy


# Setup the soap server
# Default values
URL = 'http://bugs.debian.org/cgi-bin/soap.cgi'
NS = 'Debbugs/SOAP/V1'
BTS_URL = 'http://bugs.debian.org/'


def _get_http_proxy():
    """Returns an HTTP proxy URL formatted for consumption by SOAPpy.

    SOAPpy does some fairly low-level HTTP manipulation and needs to be
    explicitly made aware of HTTP proxy URLs, which also have to be
    formatted without a schema or path.

    """
    http_proxy = urllib.getproxies().get('http')
    if http_proxy is None:
        return None
    return urlparse.urlparse(http_proxy).netloc


server = SOAPpy.SOAPProxy(URL, NS, http_proxy=_get_http_proxy())


class Bugreport(object):
    """Represents a bugreport from Debian's Bug Tracking System.

    A bugreport object provides all attributes provided by the SOAP interface.
    Most of the attributs are strings, the others are marked.

    * bug_num: The bugnumber (int)
    * severity: Severity of the bugreport
    * tags: List of tags of the bugreport (list of strings)
    * subject:  The subject/title of the bugreport
    * originator: Submitter of the bugreport
    * mergedwith: List of bugnumbers this bug was merged with (list of ints)
    * package: Package of the bugreport
    * source: Source package of the bugreport
    * date: Date of bug creation (datetime)
    * log_modified: Date of update of the bugreport (datetime)
    * done: Is the bug fixed or not (bool)
    * archived: Is the bug archived or not (bool)
    * unarchived: Was the bug unarchived or not (bool)
    * fixed_versions: List of versions, can be empty even if bug is fixed (list of strings)
    * found_versions: List of version numbers where bug was found (list of strings)
    * forwarded: A URL or email address
    * blocks: List of bugnumbers this bug blocks (list of ints)
    * blockedby: List of bugnumbers which block this bug (list of ints)
    * pending: Either 'pending' or 'done'
    * msgid: Message ID of the bugreport
    * owner: Who took responsibility for fixing this bug
    * location: Either 'db-h' or 'archive'
    * affects: List of Packagenames (list of strings)
    * summary: Arbitrary text
    """

    def __init__(self):
        self.originator = None
        self.date = None
        self.subject = None
        self.msgid = None
        self.package = None
        self.tags = None
        self.done = None
        self.forwarded = None
        self.mergedwith = None
        self.severity = None
        self.owner = None
        self.found_versions = None
        self.fixed_versions = None
        self.blocks = None
        self.blockedby = None
        self.unarchived = None
        self.summary = None
        self.affects = None
        self.log_modified = None
        self.location = None
        self.archived = None
        self.bug_num = None
        self.source = None
        self.pending = None
        # The ones below are also there but not used
        #self.fixed = None
        #self.found = None
        #self.fixed_date = None
        #self.found_date = None
        #self.keywords = None
        #self.id = None


    def __str__(self):
        s = ""
        for key, value in self.__dict__.iteritems():
            if type(value) == type(unicode()):
                value = value.encode('utf-8')
            s += "%s: %s\n" % (key, str(value))
        return s

    def __cmp__(self, other):
        """Compare a bugreport with another.

        The more open and and urgent a bug is, the greater the bug is:
            outstanding > resolved > archived
            critical > grave > serious > important > normal > minor > wishlist.
        Openness always beats urgency, eg an archived bug is *always* smaller
        than an outstanding bug.

        This sorting is useful for displaying bugreports in a list and sorting
        them in a useful way.
        """

        myval = self._get_value()
        otherval = other._get_value()
        if myval < otherval:
            return -1
        elif myval == otherval:
            return 0
        else:
            return 1


    def _get_value(self):
        if self.archived:
            # archived and done
            val = 0
        elif self.done:
            # not archived and done
            val = 10
        else:
            # not done
            val = 20
        val += {u"critical" : 7,
                u"grave" : 6,
                u"serious" : 5,
                u"important" : 4,
                u"normal" : 3,
                u"minor" : 2,
                u"wishlist" : 1}[self.severity]
        return val


def get_status(*nr):
    """Returns a list of Bugreport objects."""
    reply = server.get_status(*nr)
    # If we called get_status with one single bug, we get a single bug,
    # if we called it with a list of bugs, we get a list,
    # No available bugreports returns an enmpy list
    bugs = []
    if not reply:
        pass
    elif type(reply[0]) == type([]):
        for elem in reply[0]:
            bugs.append(_parse_status(elem))
    else:
        bugs.append(_parse_status(reply[0]))
    return bugs


def get_usertag(email, *tags):
    """Return a dictionary of "usertag" => buglist mappings.

    If tags are given the dictionary is limited to the matching tags, if no
    tags are given all available tags are returned.
    """
    reply = server.get_usertag(email, *tags)
    # reply is an empty string if no bugs match the query
    return dict() if reply == "" else reply._asdict()


def get_bug_log(nr):
    """Return a list of Buglogs.

    A buglog is a dictionary with the following mappings:
        "header" => string
        "body" => string
        "attachments" => list
        "msg_num" => int
    """
    reply = server.get_bug_log(nr)
    buglog = [i._asdict() for i in reply._aslist()]
    for b in buglog:
        b["header"] = _uc(b["header"])
        b["body"] = _uc(b["body"])
        b["msg_num"] = int(b["msg_num"])
        b["attachments"] = b["attachments"]._aslist()
    return buglog


def newest_bugs(amount):
    """Returns a list of bugnumbers of the `amount` newest bugs."""
    reply = server.newest_bugs(amount)
    return reply._aslist()


def get_bugs(*key_value):
    """Returns a list of bugnumbers, that match the conditions given by the
    key-value pair(s).

    Possible keys are:
        "package": bugs for the given package
        "submitter": bugs from the submitter
        "maint": bugs belonging to a maintainer
        "src": bugs belonging to a source package
        "severity": bugs with a certain severity
        "status": can be either "done", "forwarded", or "open"
        "tag": see http://www.debian.org/Bugs/Developer#tags for available tags
        "owner": bugs which are assigned to `owner`
        "bugs": takes list of bugnumbers, filters the list according to given criteria
        "correspondent": bugs where `correspondent` has sent a mail to

    Example: get_bugs('package', 'gtk-qt-engine', 'severity', 'normal')
    """
    reply = server.get_bugs(*key_value)
    return reply._aslist()


def _parse_status(status):
    """Return a bugreport object from a given status."""
    status = status._asdict()
    bug = Bugreport()
    tmp = status['value']

    bug.originator = _uc(tmp['originator'])
    bug.date = datetime.utcfromtimestamp(tmp['date'])
    bug.subject = _uc(tmp['subject'])
    bug.msgid = _uc(tmp['msgid'])
    bug.package = _uc(tmp['package'])
    bug.tags = _uc(tmp['tags']).split()
    bug.done = bool(tmp['done'])
    bug.forwarded = _uc(tmp['forwarded'])
    bug.mergedwith = [int(i) for i in str(tmp['mergedwith']).split()]
    bug.severity = _uc(tmp['severity'])
    bug.owner = _uc(tmp['owner'])
    bug.found_versions = [_uc(str(i)) for i in tmp['found_versions']]
    bug.fixed_versions = [_uc(str(i)) for i in tmp['fixed_versions']]
    bug.blocks = [int(i) for i in str(tmp['blocks']).split()]
    bug.blockedby = [int(i) for i in str(tmp['blockedby']).split()]
    bug.unarchived = bool(tmp["unarchived"])
    bug.summary = _uc(tmp['summary'])
    affects = tmp['affects'].strip()
    bug.affects = [_uc(i.strip()) for i in affects.split(',')] if affects else []
    bug.log_modified = datetime.utcfromtimestamp(tmp['log_modified'])
    bug.location = _uc(tmp['location'])
    bug.archived = bool(tmp["archived"])
    bug.bug_num = int(tmp['bug_num'])
    bug.source = _uc(tmp['source'])
    bug.pending = _uc(tmp['pending'])
    # Also available, but unused or broken
    #bug.fixed = _parse_crappy_soap(tmp, "fixed")
    #bug.found = _parse_crappy_soap(tmp, "found")
    #bug.found_date = [datetime.utcfromtimestamp(i) for i in tmp["found_date"]]
    #bug.fixed_date = [datetime.utcfromtimestamp(i) for i in tmp["fixed_date"]]
    #bug.keywords = _uc(tmp['keywords']).split()
    #bug.id = int(tmp['id'])
    return bug


def _uc(string):
    """Convert string to unicode.

    This method only exists to unify the unicode conversion in this module.
    """
    return unicode(string, 'utf-8', 'replace')

