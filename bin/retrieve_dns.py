#!/usr/bin/env python

#   Copyright (C) 2012 STFC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# Retrieves glite-APEL DNs from a query to GOCDB and then adds any extra
# DNs from a file.  Writes these to second file, which contains a list of
# trusted DNs.
#
# This is checked by the SSM when a message is received to see if the message
# is from a trusted source.
'''
@author: Will Rogers
'''

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from future.builtins import object, str

from apel.common import set_up_logging, LOG_BREAK
from apel import __version__

from optparse import OptionParser
import logging.config
import os
import sys
import time
import xml.dom.minidom
import xml.parsers.expat
try:
    # Renamed ConfigParser to configparser in Python 3
    # urllib code flow got changed in Python 3
    import configparser as ConfigParser
    import urllib.request
    import urllib.error
except ImportError:
    import ConfigParser
    import urllib


log = logging.getLogger('auth')


class Configuration(object):
    """Dummy class for attaching configuration to."""
    def __init__(self):
        self.gocdb_url = None
        self.extra_dns = None
        self.banned_dns = None
        self.dn_file = None
        self.proxy = None
        self.expire_hours = None

def get_config(config_file):
    """Using the config file location, get a config object."""
    # Read configuration from file
    cp = ConfigParser.ConfigParser()
    cp.read(config_file)

    c = Configuration()

    try:
        c.gocdb_url = cp.get('auth', 'gocdb_url')
    except ConfigParser.NoOptionError:
        c.gocdb_url = None

    try:
        extra_dns = cp.get('auth', 'extra-dns')
        c.extra_dns = os.path.normpath(os.path.expandvars(extra_dns))
    except ConfigParser.NoOptionError:
        c.extra_dns = None

    try:
        banned_dns = cp.get('auth', 'banned-dns')
        c.banned_dns = os.path.normpath(os.path.expandvars(banned_dns))
    except ConfigParser.NoOptionError:
        c.banned_dns = None

    try:
        dn_file = cp.get('auth', 'allowed-dns')
        c.dn_file = os.path.normpath(os.path.expandvars(dn_file))
    except ConfigParser.NoOptionError:
        c.dn_file = None

    try:
        proxy = cp.get('auth', 'proxy')
        c.proxy = proxy
    except ConfigParser.NoOptionError:
        c.proxy = None

    try:
        c.expire_hours = cp.getint('auth', 'expire_hours')
    except ConfigParser.NoOptionError:
        c.expire_hours = 0

    # set up logging
    try:
        if os.path.exists(options.log_config):
            logging.config.fileConfig(options.log_config)
        else:
            set_up_logging(cp.get('logging', 'logfile'),
                           cp.get('logging', 'level'),
                           cp.getboolean('logging', 'console'))
    except (ConfigParser.Error, ValueError, IOError) as err:
        print('Error configuring logging: %s' % str(err))
        print('The system will exit.')
        sys.exit(1)

    return c


def get_xml(url, proxy):
    '''
    Given a URL, fetch the contents.  We expect the URL to be https and
    the contents to be XML.
    '''
    if sys.version_info >= (3,):
        return execute_py3_get_xml_content(url, proxy)
    else:
        return execute_py2_get_xml_content(url, proxy)

def execute_py3_get_xml_content(url, proxy):
    """Helper method to execute python3 code for urllib code flow"""
    try:
        # Try without a proxy
        conn = urllib.request.urlopen(url)
        dn_xml = conn.read()
        conn.close()
    except urllib.error.URLError:
        # Try with a proxy
        if proxy is not None:
            proxies = {"http": proxy}
            proxyHandler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(proxyHandler)
            conn = opener.open(url)
            dn_xml = conn.read()
            conn.close()
        else:
            raise

    return dn_xml

def execute_py2_get_xml_content(url, proxy):
    """Helper method to execute python2 code for urllib code flow"""
    try:
        # Try without a proxy
        conn = urllib.urlopen(url)
        dn_xml = conn.read()
        conn.close()
    except IOError:
        # Try with a proxy
        if proxy is not None:
            proxy = {"http": proxy}
            conn = urllib.urlopen(url, proxies=proxy)
            dn_xml = conn.read()
            conn.close()
        else:
            raise

    return dn_xml


def dns_from_dom(dom):
    """
    Given a Document Object Model, get the content of all <HOSTDN> tags.

    Returns a list of strings.
    """
    dn_nodes = dom.getElementsByTagName('HOSTDN')

    log.info('Found %s HOSTDN tags.', len(dn_nodes))

    dns = []
    for dn in dn_nodes:
        # The text is a child node of the HOSTDN element.
        # We expect only one child node each time.
        children = dn.childNodes
        for node in children:
            dns.append(node.data)

    # remove any whitespace
    dns = [dn.strip() for dn in dns]

    return dns

def dns_from_file(path):
    '''
    Get all the lines in a file and return them as a list of strings.  We
    assume that they're DNs, but we'll check later.
    '''

    with open(path) as dn_file:
        dns = dn_file.readlines()
    # get rid of any whitespace in the list of strings
    dns = [dn.strip() for dn in dns]
    return dns


def next_link_from_dom(dom):
    """
    Given a Document Object Model, return the "next" link, if any, or None.

    i.e. the href of the <link rel="next" href="..."/> tag.
    """
    # First, assume there is no next link
    next_url = None

    # Get the link nodes from the DOM
    link_nodes = dom.getElementsByTagName('link')

    # For each link node, i.e. self, prev, next and start
    for link in link_nodes:
        # Find the rel value i.e <link ref="next" href="..."/>
        rel = link.attributes['rel'].value
        # Assumes only one next value
        if rel == 'next':
            # Fetch this link next
            next_url = link.attributes['href'].value

    return next_url


def verify_dn(dn):
    '''
    Simplistically check that the DN is of the /-separated format.
    '''
    # it should begin with a slash
    if dn.find('/') != 0:
        return False

    dn_components = dn.split('/')

    # Check that there are at least two parts to the DN. There should be 3 after
    # the .split as an empty string is considered to be before the leading '/'.
    if len(dn_components) <= 2:
        return False

    # Reject a DN if a component of it ends in a trailing comma.
    # i.e. don't accept `/C=Egg, /O=Bacon , /OU=Spam, /L=Lobster Thermidor`
    for component in dn_components:
        if component.endswith(", "):
            return False

    return True


def runprocess(config_file, log_config_file):
    '''Get DNs both from the URL and the additional file.'''
    cfg = get_config(config_file)

    log = logging.getLogger('auth')
    log.info(LOG_BREAK)
    log.info('Starting apel auth version %s.%s.%s', *__version__)
    log.info("Starting auth ...")

    # We'll fill this list with DNs.
    dns = []
    xml_string = None
    fetch_failed = False

    next_url = cfg.gocdb_url
    try:
        # If next_url is none, it implies we have reached the end of paging
        # (or that paging was not turned on).
        # The addition of 'not fetch_failed' catches the case where no XML is
        # returned from next_url (i.e. gocdb_url).
        while next_url is not None and not fetch_failed:
            xml_string = get_xml(next_url, cfg.proxy)
            log.info("Fetched XML from %s", next_url)

            try:
                # Parse the XML into a Document Object Model
                dom = xml.dom.minidom.parseString(xml_string)
                # Get the next url, if any
                next_url = next_link_from_dom(dom)
                # Add the listed DNs to the list
                dns.extend(dns_from_dom(dom))
            except xml.parsers.expat.ExpatError:
                log.warning('Failed to parse the retrieved XML.')
                log.warning('Is the URL correct?')
                fetch_failed = True
    except AttributeError:
        # gocdb_url is None
        log.info("No GOCDB URL specified - won't fetch URLs.")
    except IOError as e:
        log.info("Failed to retrieve XML - is the URL correct?")
        log.info(e)
        fetch_failed = True

    if fetch_failed and (time.time() - os.path.getmtime(cfg.dn_file) <
                         (cfg.expire_hours * 3600)):
        log.warning('Failed to update DNs from GOCDB. Will not modify DNs file.')
        log.info("auth will exit.")
        log.info(LOG_BREAK)
        sys.exit(1)

    # get the DNs from the additional file
    try:
        extra_dns = dns_from_file(cfg.extra_dns)
        log.info("Fetched %s extra DNs from file %s.", len(extra_dns), cfg.extra_dns)
        dns.extend(extra_dns)
    except IOError:
        log.warning("Failed to retrieve extra DNs from file %s.", cfg.extra_dns)
        log.warning("Check the configuration.")

    dns_to_remove = []
    try:
        dns_to_remove = dns_from_file(cfg.banned_dns)
        log.info("Fetched %s banned DNs from file %s.", len(dns_to_remove), cfg.banned_dns)
    except IOError:
        log.warning("Failed to retrieve banned DNs from file %s.", cfg.banned_dns)
        log.warning("Check the configuration.")

    # remove all items from the list dns which are in the list dns_to_remove
    dns = [ dn for dn in dns if dn not in dns_to_remove ]

    # print all the the dns to a file, with the discarded ones to a second file
    try:
        new_dn_file = open(cfg.dn_file, 'w')
    except IOError:
        log.warning("Failed to open file %s for writing.", cfg.dn_file)
        log.warning("Check the configuration.")
        log.warning("auth will exit.")
        log.info(LOG_BREAK)
        sys.exit(1)

    added = 0
    for dn in dns:
        if verify_dn(dn):
            new_dn_file.write(dn)
            new_dn_file.write('\n')
            added += 1
        elif dn.lstrip().startswith("#"):
            # Ignore comment lines starting with "#"
            log.debug("Comment ignored: %s", dn)
        else:
            # We haven't accepted the DN, so write it to the log file.
            log.warning("DN not valid and won't be added: %s", dn)

    new_dn_file.close()

    log.info("%s DNs have been written to %s.", added, cfg.dn_file)

    log.info("auth has finished.")
    log.info(LOG_BREAK)


if __name__ == '__main__':
    ver = "APEL auth %s.%s.%s" % __version__
    opt_parser = OptionParser(description=__doc__, version=ver)
    opt_parser.add_option('-c', '--config', help='location of the config file',
                          default='/etc/apel/auth.cfg')
    opt_parser.add_option('-l', '--log_config', help='Location of logging config file (optional)',
                          default='/etc/apel/logging.cfg')
    (options, args) = opt_parser.parse_args()

    runprocess(options.config, options.log_config)
