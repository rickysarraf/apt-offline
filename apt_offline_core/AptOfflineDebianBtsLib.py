#!/usr/bin/env python

"""
Query Debian's Bug Tracking System (BTS).

This module provides a layer between Python and Debian's BTS. It
provides methods to query the BTS using the BTS' SOAP interface, and the
Bugreport class which represents a bugreport from the BTS.
"""


import base64
from distutils.version import LooseVersion
import email.feedparser
import email.policy
from datetime import datetime
import os
import sys
import logging

import pysimplesoap
from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement


logger = logging.getLogger(__name__)


# Support running from Debian infrastructure
ca_path = '/etc/ssl/ca-debian'
if os.path.isdir(ca_path):
    os.environ['SSL_CERT_DIR'] = ca_path


PYSIMPLESOAP_1_16_2 = (LooseVersion(pysimplesoap.__version__) >=
                       LooseVersion('1.16.2'))

# Setup the soap server
# Default values
URL = 'https://bugs.debian.org/cgi-bin/soap.cgi'
NS = 'Debbugs/SOAP/V1'
BTS_URL = 'https://bugs.debian.org/'
# Max number of bugs to send in a single get_status request
BATCH_SIZE = 500

SEVERITIES = {
    'critical': 7,
    'grave': 6,
    'serious': 5,
    'important': 4,
    'normal': 3,
    'minor': 2,
    'wishlist': 1,
}


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
    done_by : str or None
        Name and Email or None
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

    def __str__(self):
        s = '\n'.join('{}: {}'.format(key, value)
                      for key, value in self.__dict__.items())
        return s + '\n'

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
        val += SEVERITIES[self.severity]
        return val


def get_status(nrs, *additional):
    """Returns a list of Bugreport objects.

    Given a list of bugnumbers this method returns a list of Bugreport
    objects.

    Parameters
    ----------
    nrs : int or list of ints
        The bugnumbers
    additional : int
        Deprecated! The remaining positional arguments are treated as
        bugnumbers. This is deprecated since 2.10.0, please use the
        `nrs` parameter instead.

    Returns
    -------
    bugs : list of Bugreport objects

    """
    if not isinstance(nrs, (list, tuple)):
        nrs = [nrs]
    # backward compatible with <= 2.10.0
    if additional:
        logger.warning('Calling get_status with bugnumbers as positional'
                       ' arguments is deprecated, please use a list instead.')
        nrs.extend(additional)

    # Process the input in batches to avoid hitting resource limits on
    # the BTS
    soap_client = _build_soap_client()
    bugs = []
    for i in range(0, len(nrs), BATCH_SIZE):
        slice_ = nrs[i:i + BATCH_SIZE]
        # I build body by hand, pysimplesoap doesn't generate soap Arrays
        # without using wsdl
        method_el = SimpleXMLElement('<get_status></get_status>')
        _build_int_array_el('arg0', method_el, slice_)
        reply = soap_client.call('get_status', method_el)
        for bug_item_el in reply('s-gensym3').children() or []:
            bug_el = bug_item_el.children()[1]
            bugs.append(_parse_status(bug_el))
    return bugs


def get_usertag(email, tags=None, *moretags):
    """Get buglists by usertags.

    Parameters
    ----------
    email : str
    tags : list of strings
        If tags are given the dictionary is limited to the matching
        tags, if no tags are given all available tags are returned.
    moretags : str
        Deprecated! The remaining positional arguments are treated as
        tags. This is deprecated since 2.10.0, please use the `tags`
        parameter instead.

    Returns
    -------
    mapping : dict
        a mapping of usertag -> buglist

    """
    if tags is None:
        tags = []
    # backward compatible with <= 2.10.0
    if not isinstance(tags, (list, tuple)):
        tags = [tags]
    if moretags:
        logger.warning('Calling get_getusertag with tags as positional'
                       ' arguments is deprecated, please use a list instead.')
        tags.extend(moretags)

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
            tag = str(usertag_el('key'))
            buglist_el = usertag_el('value')
            mapping[tag] = [int(bug) for bug in buglist_el.children() or []]
    else:
        for usertag_el in map_el.children() or []:
            tag = usertag_el.get_name()
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

        mail_parser = email.feedparser.BytesFeedParser(
            policy=email.policy.SMTP
        )
        mail_parser.feed(buglog["header"].encode())
        mail_parser.feed("\n\n".encode())
        mail_parser.feed(buglog["body"].encode())
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


def get_bugs(*key_value, **kwargs):
    """Get list of bugs matching certain criteria.

    The conditions are defined by the keyword arguments.

    Arguments
    ---------
    key_value : str
        Deprecated! The positional arguments are treated as key-values.
        This is deprecated since 2.10.0, please use the `kwargs`
        parameters instead.
    kwargs :
        Possible keywords are:
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
            * "archive": takes a string: "0" (unarchived), "1"
              (archived) or "both" (un- and archived). if omitted, only
              returns un-archived bugs.

    Returns
    -------
    bugs : list of ints
        the bugnumbers

    Examples
    --------
    >>> get_bugs(package='gtk-qt-engine', severity='normal')
    [12345, 23456]

    """
    # flatten kwargs to list:
    # {'foo': 'bar', 'baz': 1} -> ['foo', 'bar','baz', 1]
    args = []
    for k, v in kwargs.items():
        args.extend([k, v])

    # previous versions also accepted
    # get_bugs(['package', 'gtk-qt-engine', 'severity', 'normal'])
    # if key_value is a list in a one elemented tuple, remove the
    # wrapping list
    if len(key_value) == 1 and isinstance(key_value[0], list):
        key_value = tuple(key_value[0])

    if key_value:
        logger.warning('Calling get_bugs with positional arguments is'
                       ' deprecated, please use keyword arguments instead.')
        args.extend(key_value)

    # pysimplesoap doesn't generate soap Arrays without using wsdl
    # I build body by hand, converting list to array and using standard
    # pysimplesoap marshalling for other types
    method_el = SimpleXMLElement('<get_bugs></get_bugs>')
    for arg_n, kv in enumerate(args):
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
    bug.tags = [tag for tag in str(bug_el('tags')).split()]
    bug.done = _parse_bool(bug_el('done'))
    bug.done_by = _parse_string_el(bug_el('done')) if bug.done else None
    bug.archived = _parse_bool(bug_el('archived'))
    bug.unarchived = _parse_bool(bug_el('unarchived'))
    bug.bug_num = int(bug_el('bug_num'))
    bug.mergedwith = [int(i) for i in str(bug_el('mergedwith')).split()]
    bug.blockedby = [int(i) for i in str(bug_el('blockedby')).split()]
    bug.blocks = [int(i) for i in str(bug_el('blocks')).split()]

    bug.found_versions = [str(el) for el in
                          bug_el('found_versions').children() or []]
    bug.fixed_versions = [str(el) for el in
                          bug_el('fixed_versions').children() or []]
    affects = [_f for _f in str(bug_el('affects')).split(',') if _f]
    bug.affects = [a.strip() for a in affects]
    # Also available, but unused or broken
    # bug.keywords = [keyword for keyword in
    #                 str(bug_el('keywords')).split()]
    # bug.fixed = _parse_crappy_soap(tmp, "fixed")
    # bug.found = _parse_crappy_soap(tmp, "found")
    # bug.found_date = \
    #     [datetime.utcfromtimestamp(i) for i in tmp["found_date"]]
    # bug.fixed_date = \
    #     [datetime.utcfromtimestamp(i) for i in tmp["fixed_date"]]
    return bug


# to support python 3.4.3, when using httplib2 as pysimplesoap transport
# we must work around a bug in httplib2, which uses
# http.client.HTTPSConnection with check_hostname=True, but with an
# empty ssl context that prevents the certificate verification. Passing
# `cacert` to httplib2 through pysimplesoap permits to create a valid
# ssl context.
_soap_client_kwargs = {
    'location': URL,
    'action': '',
    'namespace': NS,
    'soap_ns': 'soap'
}
if sys.version_info.major == 3 and sys.version_info < (3, 4, 3):
    try:
        from httplib2 import CA_CERTS
    except ImportError:
        pass
    else:
        _soap_client_kwargs['cacert'] = CA_CERTS


def set_soap_proxy(proxy_arg):
    """Set proxy for SOAP client.

    You must use this method after import to set the proxy.

    Parameters
    ----------
    proxy_arg : str

    """
    _soap_client_kwargs['proxy'] = proxy_arg


def set_soap_location(url):
    """Set location URL for SOAP client

    You may use this method after import to override the default URL.

    Parameters
    ----------
    url : str

    """
    _soap_client_kwargs['location'] = url


def get_soap_client_kwargs():
    return _soap_client_kwargs


def _build_soap_client():
    """Factory method that creates a SoapClient.

    For thread-safety we create SoapClients on demand instead of using a
    module-level one.

    Returns
    -------
    sc : SoapClient instance

    """
    return SoapClient(**_soap_client_kwargs)


def _convert_soap_method_args(*args):
    """Convert arguments to be consumed by a SoapClient method

    Soap client required a list of named arguments:
    >>> _convert_soap_method_args('a', 1)
    [('arg0', 'a'), ('arg1', 1)]

    """
    soap_args = []
    for arg_n, arg in enumerate(args):
        soap_args.append(('arg' + str(arg_n), arg))
    return soap_args


def _soap_client_call(method_name, *args):
    """Wrapper to call SoapClient method"""
    # a new client instance is built for threading issues
    soap_client = _build_soap_client()
    soap_args = _convert_soap_method_args(*args)
    # if pysimplesoap version requires it, apply a workaround for
    # https://github.com/pysimplesoap/pysimplesoap/issues/31
    if PYSIMPLESOAP_1_16_2:
        return getattr(soap_client, method_name)(*soap_args)
    else:
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
        value = value.decode('utf-8', errors='replace')
    return value
