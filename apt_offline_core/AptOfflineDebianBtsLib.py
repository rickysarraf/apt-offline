#!/usr/bin/env python

# debianbts.py - Methods to query Debian's BTS.
# Copyright (C) 2007-2015  Bastian Venthur <venthur@debian.org>
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


"""
Query Debian's Bug Tracking System (BTS).

This module provides a layer between Python and Debian's BTS. It
provides methods to query the BTS using the BTS' SOAP interface, and the
Bugreport class which represents a bugreport from the BTS.
"""


from __future__ import division, unicode_literals, absolute_import, print_function

import base64
import email.feedparser
from datetime import datetime
import os
import sys

from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement

# Support running from Debian infrastructure
ca_path = '/etc/ssl/ca-debian'
if os.path.isdir(ca_path):
    os.environ['SSL_CERT_DIR'] = ca_path


# please follow the semver semantics, i.e. MAJOR.MINOR.PATCH where
# MAJOR: incompatible API changes
# MINOR: add backwards-comptible functionality
# PATCH: backwards-compatible bug fixes.
__version__ = '2.6.0'


PY2 = sys.version_info.major == 2

# Setup the soap server
# Default values
URL = 'https://bugs.debian.org/cgi-bin/soap.cgi'
NS = 'Debbugs/SOAP/V1'
BTS_URL = 'https://bugs.debian.org/'
# Max number of bugs to send in a single get_status request
BATCH_SIZE = 500



class Bugreport(object):
    """Represents a bugreport from Debian's Bug Tracking System.

    A bugreport object provides all attributes provided by the SOAP
    interface. Most of the attributes are strings, the others are
    marked.

    Attributes
    ----------

    bug_num : int
        The bugnumber
    severity : str
        Severity of the bugreport
    tags : list of strings
        Tags of the bugreport
    subject : str
        The subject/title of the bugreport
    originator : str
        Submitter of the bugreport
    mergedwith : list of ints
        List of bugnumbers this bug was merged with
    package : str
        Package of the bugreport
    source : str
        Source package of the bugreport
    date : datetime
        Date of bug creation
    log_modified : datetime
        Date of update of the bugreport
    done : boolean
        Is the bug fixed or not
    archived : bool
        Is the bug archived or not
    unarchived : bool
        Was the bug unarchived or not
    fixed_versions : list of strings
        List of versions, can be empty even if bug is fixed
    found_versions : list of strings
        List of version numbers where bug was found
    forwarded : str
        A URL or email address
    blocks: list of ints
        List of bugnumbers this bug blocks
    blockedby : list of int
        List of bugnumbers which block this bug
    pending : str
        Either 'pending' or 'done'
    msgid : str
        Message ID of the bugreport
    owner : str
        Who took responsibility for fixing this bug
    location : str
        Either 'db-h' or 'archive'
    affects : list of str
        List of Packagenames
    summary : str
        Arbitrary text
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
        # self.fixed = None
        # self.found = None
        # self.fixed_date = None
        # self.found_date = None
        # self.keywords = None
        # self.id = None

    def __unicode__(self):
        s = '\n'.join('{}: {}'.format(key, value)
                       for key, value in self.__dict__.items())
        return s + '\n'

    if PY2:
        def __str__(self):
            return self.__unicode__().encode('utf-8')
    else:
        __str__ = __unicode__

    def __lt__(self, other):
        """Compare a bugreport with another.

        The more open and urgent a bug is, the greater the bug is:

            outstanding > resolved > archived

            critical > grave > serious > important > normal > minor > wishlist.

        Openness always beats urgency, eg an archived bug is *always*
        smaller than an outstanding bug.

        This sorting is useful for displaying bugreports in a list and
        sorting them in a useful way.

        """
        return self._get_value() < other._get_value()

    def __le__(self, other):
        return not self.__gt__(other)

    def __gt__(self, other):
        return self._get_value() > other._get_value()

    def __ge__(self, other):
        return not self.__lt__(other)

    def __eq__(self, other):
        return self._get_value() == other._get_value()

    def __ne__(self, other):
        return not self.__eq__(other)

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
        val += {"critical": 7,
                "grave": 6,
                "serious": 5,
                "important": 4,
                "normal": 3,
                "minor": 2,
                "wishlist": 1}[self.severity]
        return val


def get_status(*nrs):
    """Returns a list of Bugreport objects.

    Given a list of bugnumbers this method returns a list of Bugreport
    objects.

    Parameters
    ----------
    nrs : int or list of ints
        the bugnumbers

    Returns
    -------
    bugs : list of Bugreport objects

    """
    # If we called get_status with one single bug, we get a single bug,
    # if we called it with a list of bugs, we get a list,
    # No available bugreports returns an empty list
    bugs = []
    list_ = []
    for nr in nrs:
        if isinstance(nr, list):
            list_.extend(nr)
        else:
            list_.append(nr)
    # Process the input in batches to avoid hitting resource limits on the BTS
    soap_client = _build_soap_client()
    for i in range(0, len(list_), BATCH_SIZE):
        slice_ = list_[i:i + BATCH_SIZE]
        # I build body by hand, pysimplesoap doesn't generate soap Arrays
        # without using wsdl
        method_el = SimpleXMLElement('<get_status></get_status>')
        _build_int_array_el('arg0', method_el, slice_)
        reply = soap_client.call('get_status', method_el)
        for bug_item_el in reply('s-gensym3').children() or []:
            bug_el = bug_item_el.children()[1]
            bugs.append(_parse_status(bug_el))
    return bugs


def get_usertag(email, *tags):
    """Get buglists by usertags.

    Parameters
    ----------
    email : str
    tags : tuple of strings
        If tags are given the dictionary is limited to the matching
        tags, if no tags are given all available tags are returned.

    Returns
    -------
    mapping : dict
        a mapping of useertag -> buglist

    """
    reply = _soap_client_call('get_usertag', email, *tags)
    map_el = reply('s-gensym3')
    mapping = {}
    # element <s-gensys3> in response can have standard type
    # xsi:type=apachens:Map (example, for email debian-python@lists.debian.org)
    # OR no type, in this case keys are the names of child elements and
    # the array is contained in the child elements
    type_attr = map_el.attributes().get('xsi:type')
    if type_attr and type_attr.value == 'apachens:Map':
        for usertag_el in map_el.children() or []:
            tag = _uc(str(usertag_el('key')))
            buglist_el = usertag_el('value')
            mapping[tag] = [int(bug) for bug in buglist_el.children() or []]
    else:
        for usertag_el in map_el.children() or []:
            tag = _uc(usertag_el.get_name())
            mapping[tag] = [int(bug) for bug in usertag_el.children() or []]
    return mapping


def get_bug_log(nr):
    """Get Buglogs.

    A buglog is a dictionary with the following mappings:
        * "header" => string
        * "body" => string
        * "attachments" => list
        * "msg_num" => int
        * "message" => email.message.Message

    Parameters
    ----------
    nr : int
        the bugnumber

    Returns
    -------
    buglogs : list of dicts

    """
    reply = _soap_client_call('get_bug_log', nr)
    items_el = reply('soapenc:Array')
    buglogs = []
    for buglog_el in items_el.children():
        buglog = {}
        buglog["header"] = _parse_string_el(buglog_el("header"))
        buglog["body"] = _parse_string_el(buglog_el("body"))
        buglog["msg_num"] = int(buglog_el("msg_num"))
        # server always returns an empty attachments array ?
        buglog["attachments"] = []

        mail_parser = email.feedparser.FeedParser()
        mail_parser.feed(buglog["header"])
        mail_parser.feed(buglog["body"])
        buglog["message"] = mail_parser.close()

        buglogs.append(buglog)
    return buglogs


def newest_bugs(amount):
    """Returns the newest bugs.

    This method can be used to query the BTS for the n newest bugs.

    Parameters
    ----------
    amount : int
        the number of desired bugs. E.g. if `amount` is 10 the method
        will return the 10 latest bugs.

    Returns
    -------
    bugs : list of int
        the bugnumbers

    """
    reply = _soap_client_call('newest_bugs', amount)
    items_el = reply('soapenc:Array')
    return [int(item_el) for item_el in items_el.children() or []]


def get_bugs(*key_value):
    """Get list of bugs matching certain criteria.

    The conditions are defined by key value pairs.

    Possible keys are:
        * "package": bugs for the given package
        * "submitter": bugs from the submitter
        * "maint": bugs belonging to a maintainer
        * "src": bugs belonging to a source package
        * "severity": bugs with a certain severity
        * "status": can be either "done", "forwarded", or "open"
        * "tag": see http://www.debian.org/Bugs/Developer#tags for
           available tags
        * "owner": bugs which are assigned to `owner`
        * "bugs": takes single int or list of bugnumbers, filters the list
           according to given criteria
        * "correspondent": bugs where `correspondent` has sent a mail to

    Arguments
    ---------
    key_value : str

    Returns
    -------
    bugs : list of ints
        the bugnumbers

    Examples
    --------
    >>> get_bugs('package', 'gtk-qt-engine', 'severity', 'normal')
    [12345, 23456]

    """
    # previous versions also accepted get_bugs(['package', 'gtk-qt-engine', 'severity', 'normal'])
    # if key_value is a list in a one elemented tuple, remove the
    # wrapping list
    if len(key_value) == 1 and isinstance(key_value[0], list):
        key_value = tuple(key_value[0])

    # pysimplesoap doesn't generate soap Arrays without using wsdl
    # I build body by hand, converting list to array and using standard
    # pysimplesoap marshalling for other types
    method_el = SimpleXMLElement('<get_bugs></get_bugs>')
    for arg_n, kv in enumerate(key_value):
        arg_name = 'arg' + str(arg_n)
        if isinstance(kv, (list, tuple)):
            _build_int_array_el(arg_name, method_el, kv)
        else:
            method_el.marshall(arg_name, kv)

    soap_client = _build_soap_client()
    reply = soap_client.call('get_bugs', method_el)
    items_el = reply('soapenc:Array')
    return [int(item_el) for item_el in items_el.children() or []]


def _parse_status(bug_el):
    """Return a bugreport object from a given status xml element"""
    bug = Bugreport()

    # plain fields
    for field in ('originator', 'subject', 'msgid', 'package', 'severity',
                  'owner', 'summary', 'location', 'source', 'pending',
                  'forwarded'):
        setattr(bug, field, _parse_string_el(bug_el(field)))

    bug.date = datetime.utcfromtimestamp(float(bug_el('date')))
    bug.log_modified = datetime.utcfromtimestamp(float(bug_el('log_modified')))
    bug.tags = [_uc(tag) for tag in str(bug_el('tags')).split()]
    bug.done = _parse_bool(bug_el('done'))
    bug.archived = _parse_bool(bug_el('archived'))
    bug.unarchived = _parse_bool(bug_el('unarchived'))
    bug.bug_num = int(bug_el('bug_num'))
    bug.mergedwith = [int(i) for i in str(bug_el('mergedwith')).split()]
    bug.blockedby = [int(i) for i in str(bug_el('blockedby')).split()]
    bug.blocks = [int(i) for i in str(bug_el('blocks')).split()]

    bug.found_versions = [_uc(str(el)) for el in
                          bug_el('found_versions').children() or []]
    bug.fixed_versions = [_uc(str(el)) for el in
                          bug_el('fixed_versions').children() or []]
    affects = [_f for _f in str(bug_el('affects')).split(',') if _f]
    bug.affects = [_uc(a).strip() for a in affects]
    # Also available, but unused or broken
    # bug.keywords = [_uc(keyword) for keyword in
    #                 str(bug_el('keywords')).split()]
    # bug.fixed = _parse_crappy_soap(tmp, "fixed")
    # bug.found = _parse_crappy_soap(tmp, "found")
    # bug.found_date = [datetime.utcfromtimestamp(i) for i in tmp["found_date"]]
    # bug.fixed_date = [datetime.utcfromtimestamp(i) for i in tmp["fixed_date"]]
    return bug


def _build_soap_client():
    """Factory method that creates a SoapClient.

    For thread-safety we create SoapClients on demand instead of using a
    module-level one.

    Returns
    -------
    sc : SoapClient instance

    """
    return SoapClient(location=URL, namespace=NS, soap_ns='soap')


def _soap_client_call(method_name, *args):
    """wrapper to work around a pysimplesoap bug
    https://github.com/pysimplesoap/pysimplesoap/issues/31"""
    soap_client = _build_soap_client()
    soap_args = []
    for arg_n, arg in enumerate(args):
        soap_args.append(('arg' + str(arg_n), arg))
    return getattr(soap_client, method_name)(soap_client, *soap_args)


def _build_int_array_el(el_name, parent, list_):
    """build a soapenc:Array made of ints called `el_name` as a child
    of `parent`"""
    el = parent.add_child(el_name)
    el.add_attribute('xmlns:soapenc',
                     'http://schemas.xmlsoap.org/soap/encoding/')
    el.add_attribute('xsi:type', 'soapenc:Array')
    el.add_attribute('soapenc:arrayType', 'xsd:int[{:d}]'.format(len(list_)))
    for item in list_:
        item_el = el.add_child('item', str(item))
        item_el.add_attribute('xsi:type', 'xsd:int')
    return el


def _parse_bool(el):
    """parse a boolean value from a xml element"""
    value = str(el)
    return not value.strip() in ('', '0')


def _parse_string_el(el):
    """read a string element, maybe encoded in base64"""
    value = str(el)
    el_type = el.attributes().get('xsi:type')
    if el_type and el_type.value == 'xsd:base64Binary':
        value = base64.b64decode(value)
        if not PY2:
            value = value.decode('utf-8')
    value = _uc(value)
    return value


"""
Convert string to unicode.

This method only exists to unify the unicode conversion in this module.
"""
if PY2:
    def _uc(string):
        return string.decode('utf-8', 'replace')
else:
    def _uc(string):
        return string
