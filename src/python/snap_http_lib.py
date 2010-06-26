"""
RESTx: Sane, simple and effective data publishing and integration. 

Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com

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

"""

# $SnapHashLicense:
# 
# SnapLogic - Open source data services
# 
# Copyright (C) 2008-2009, SnapLogic, Inc.  All rights reserved.
# 
# See http://www.snaplogic.org for more information about
# the SnapLogic project. 
# 
# This program is free software, distributed under the terms of
# the GNU General Public License Version 2. See the LEGAL file
# at the top of the source tree.
# 
# "SnapLogic" is a trademark of SnapLogic, Inc.
# 
# 
# $

# $Id: snap_http_lib.py 6844 2009-03-18 01:05:10Z jbrendel $

'''
    Our own HTTP library, which ensures a single, low-level
    interface for HTTP client tasks. One could use urllib or urllib2
    or httplib - and we did - but then you end up with all those
    different libaries doing the same thing, just differently.

    So, here we now have a single, unified interface that we can
    use for all HTTP client tasks.
'''

import urlparse
import string
import httplib
import base64
import urllib
import re
import socket

VALID_URI_PATH_RE = re.compile(r'^[/a-zA-Z0-9_\.]+$')

def check_relative_uri(uri, error_uri=None):
    """
    Checks that a relative URI is properly formatted.
    
    If the URI is not properly formatted an exception is raised. If error_uri is given and not None,
    this URI will be used to generate the exception error message instead of the relative URI given
    by uri.
    
    @param uri: A relative URI.
    @type uri: str
    
    @param error_uri: The URI to use for error message or None to use the uri parameter.
    @type error_uri: str
    
    @raise SnapValueError: The URI is incorrectly formatted or not relative.
    
    """
    if error_uri is None:
        error_uri = uri

    # First remove the query string portion from the URI if it exists
    uri = uri.split('?', 1)[0]
    if not uri.startswith('/'):
        raise Exception("'%s' is not a relative URI" % error_uri)
    elif uri.find('//') != -1:
        raise Exception("'%s' path cannot contain '//'" % error_uri)
    elif not VALID_URI_PATH_RE.match(uri):
        raise Exception("'%s' path contains invalid characters" % error_uri)

def unparse_uri((scheme, netloc, url, params, query, fragment)):
    """Unparses a URI similar to L{urlparse.urlunparse)."""
    return urlparse.urlunparse((scheme, netloc, url, params, query, fragment))
    
def parse_uri(uri, default_scheme=None, require_absolute=False):
    """
    Parses a URI like urlparse but wih additional error checking.
    
    Parses a URI and returns results in exactly the same format as urlparse.urlparse(). Unlike urlparse
    that tries to recover from poorly formatted URIs, more strict checking is performed and in the case
    of error this method throws an exception.
    
    @param uri: A relative or absolute URI.
    @type uri: str
    
    @param require_absolute: A flag indicating if the URI must be absolute.
    @type require_absolute: bool
    
    @return: The return is the same as that of urlparse.urlparse--a tuple. See the python documentation for
             urlparse for details.
    @rtype: tuple
    
    @raise SnapValueError: The URI is malformed or not absolute and the require_absolute flag is True.
    
    """
    uri = uri.strip()
    if uri.startswith('/'):
        if require_absolute:
            raise Exception("'%s' must be an absolute URI" % uri)
        else:
            check_relative_uri(uri)
            return urlparse.urlparse(uri, default_scheme)
    else:
        parsed = urlparse.urlparse(uri, default_scheme)
        if not parsed.hostname:
            raise Exception("'%s' missing required hostname" % uri)
        elif parsed.path:
            check_relative_uri(parsed.path, uri)
            
        return parsed

def parse_host_and_path(url):
    idx = url.find("://")
    idx = url.find('/',idx + 3)
    host = url[:idx]
    path = url[idx:]
    return (host,path)

def is_ip_address(label):
    """Returns true if the string is in dotted decimal format."""
    l = label.split(".")
    if (len(l) == 4 and l[0].isdigit() and l[1].isdigit() and l[2].isdigit() and l[3].isdigit()):
        return True
    
    return False

def is_localhost(host):
    """Return True if host is 'localhost' or '127.0.0.1'."""
    h = host.lower()
    if (h == "localhost") or h.startswith("localhost.") or (is_ip_address(h) and h.startswith("127")):
        return True
    else:
        return False


def parseHostAndScheme(url):
    """
    Separates out URL into scheme, location  and rest of URL.
    
    This method is useful when rest of URL has special characters
    that have not been encoded and would return invalid tuples with
    urlpars.urlsparse()
    
    @param url: URL being parsed
    @type url:  string
    
    @return: (scheme, location, rest of URL). If the URL is not an
        absolute http URL, then (None, None, url) is returned.
    @rtype:  3-tuple
    
    @raise SnapFormatError: If URL has invalid format.
    
    """

    is_http = is_https = False

    lower_url = url.lower()
    if lower_url.startswith("http://"):
        is_http  = True
        min_len  = 8
        find_idx = 7
        scheme   = "http"
    elif lower_url.startswith("https://"):
        is_https = True
        min_len  = 9
        find_idx = 8
        scheme   = "https"
    else:
        # It's a relative URL
        return (None, None, url)
    
    if len(url) < min_len:
        raise Exception("Resource URL %s has invalid format" % url)
    
    idx = url.find('/', find_idx)
    if idx < 0:
        raise Exception("Resource URL %s has invalid format" % url)
    
    loc = url[find_idx:idx]
    if len(loc) == 0:
        raise Exception("Resource URL %s has invalid format" % url)
    
    path = url[idx:]
    if not len(path):
        raise Exception("Resource URL %s has invalid format" % url)
    
    return (scheme, loc, path)


def concat_paths(*paths):
    """Concatenate path elements. Currently does not handle params"""
    
    # First remove all trailing and leading slashes in path elements.
    paths = [p.lstrip("/") for p in paths]
    paths = [p.rstrip("/") for p in paths]
    sch,loc,path,param,query,frag = urlparse.urlparse("/".join(paths))
    if not path.startswith("/"):
        path = "/" + path
    return urlparse.urlunparse((sch,loc,path,"","",""))
    
    
def get_host_port_from_uri(uri):
    """
    Get host port and scheme from URI.
    
    @param uri:  URI to be parsed.
    @type uri:   str
    
    @return: Tuple containing (host, port, scheme)
    @rtype:  tuple
    
    """
    sch,loc,path,param,query,frag =  urlparse.urlparse(uri)
    
    s = loc.split(":")
    if len(s) == 2:
        port = int(s[1])
        host = s[0]
    elif len(s) == 1:
        port = None
        host = s[0]
    else:
        raise Exception("Invalid URI %s" % uri)
        
    if port is None:
        if sch.lower() == "http":
            port = 80
        elif sch.lower() == "https":
            port = 443
    
    return (host, port, sch)

def add_params_to_uri(uri, params_dict):
    """
    Add params to the URI.
    
    If the URI already has certain params, then this function adds to those params. The key 
    and value of the new params are quoted.
    
    @param uri: URI that needs appending
    @type uri:  str
    
    @param params_dict: Dictionary of new params
    @type params_dict:  dict
    
    @return: The modified URI
    @rtype:  str
    
    """
      
    sch,loc,path,param,query,frag =  urlparse.urlparse(uri)
    for k in params_dict:
        if params_dict[k] is None:
            params_dict[k] = ""
    new_params = ["%s=%s" % (urllib.quote(k) , urllib.quote(params_dict[k])) for k in params_dict]
    if query:
        new_params += query.split("&")

    query = "&".join(new_params)
    
    return urlparse.urlunparse((sch,loc,path,param,query,frag))

def get_params_from_uri(uri):
    """
    Parse a URI and return its params as a dictionary.
    
    @param uri: URI that needs to be parsed
    @type uri:  str 
    
    @return: Dictionary of params.
    @rtype:  dict
    
    """
    sch,loc,path,param,query,frag = urlparse.urlparse(uri)
    ret = {}
    if query:
        params = query.split("&")
        for p in params:
            items = p.split('=')
            key_val = [urllib.unquote_plus(i) for i in items]
            if len(key_val) == 1:
                key_val.append(None)
            ret[key_val[0]] = key_val[1]
    return ret


def get_all_ip_addresses(hostname):
    """
    Return all IP addresses for given host name.
    
    @param hostname: Name of the host
    @type hostname:  str
    
    @return: List of ip addresses.
    @rtype:  list
    
    """
    
    result = socket.getaddrinfo(hostname, None, 0, socket.SOCK_STREAM)
    return [x[4][0] for x in result]
    
def gather_local_host_ips(other_hosts):
    """This method does a best effort in figuring out all the IP addresses on the local host and returns it."""
    ret = set()
    host_list = [socket.gethostname(), 'localhost']
    host_list.extend(other_hosts)
    
    for h in host_list:
        ret.update(get_all_ip_addresses(h))
    
    return ret
    
def uri_refers_to(uri, hostname_list, port):
    """
    Return True, if the hostname(s) and port specified are the same as the ones specified in the uri.
    
    The issue being handled in this method is how do we match hostname specified in one URI
    with the hostname specified, if machines can have multiple hostnames and multiple ip addresses.
    
    @param uri: URI that needs to be tested with host and port provided.
    @type uri:  str
    
    @param hostname: Name of the host.
    @type hostname:  str
    
    @param port: Port number
    @type port:  str
    
    @return: True if the URI points to the host and port specified, False otherwise.
    
    """

    (uri_host, uri_port, uri_scheme) = get_host_port_from_uri(uri)
    if uri_port != int(port):
        # Ports don't match.
        return False
    
    # We will convert all hostnames to the list of IP addresses
    # and see if there is a match at the IP address level.
    
    # First create list of IP addresses for the hsotname specified in the URI
    if not is_ip_address(uri_host):
        uri_ips = set(get_all_ip_addresses(uri_host))
    else:
        uri_ips = set([uri_host])
    
    # next, do the same for the hostnames supplied by the caller.
    ips = set()
    for h in hostname_list:
        if not is_ip_address(h):
            ips.update(get_all_ip_addresses(h))
        else:
            ips.add(h)
    
    if len(ips.intersection(uri_ips)) > 0:
        return True
    
    return False

class _HttpAuthenticationHolder:
    _username = None
    _password = None

    @classmethod
    def _setUsernamePassword(cls, username, password):
        _HttpAuthenticationHolder._username = username
        _HttpAuthenticationHolder._password = password

    @classmethod
    def _getUsernamePassword(cls, ):
        return (_HttpAuthenticationHolder._username, _HttpAuthenticationHolder._password)


class HttpResponse:

    InstanceCounter = 0

    @classmethod
    def _getNextInstanceCounter(self):
        HttpResponse.InstanceCounter += 1
        return HttpResponse.InstanceCounter

    def __init__(self, get_response_now, connection, my_instance_counter, dbg_str=None):
        '''
            Takes the HTTPConnection object as initializer.
            The dbg_str is printed when the connection is closed,
            if it is something other than None. The get_response_now
            flag indicates whether we should try to receive the response
            from the server right here, or leave this to the user for
            later. Finally, the my_instance_counter is mostly used
            for internal tracking and debugging.

            In general: A user should not try to create this kind
            of object on its own. The urlopn() and sendreq() functions
            of this module are the only ones who should do so.
        '''
        try:
            self.__connection = connection
            self.__counter    = my_instance_counter
            if get_response_now:
                self.__response = connection.getresponse()
            else:
                self.__response = None
            self.__headers    = None
            self.__dbg_str    = dbg_str
        except Exception, e:
            print "SnapHttpLib.HttpResponse.__init__(): Exception: " + str(e)
            raise e
        
    def sock():
        """The socket inside HttpConnection of HttpResponse (depending on object which is active)"""
        doc = "Socket wrapped by HttpResponse or HttpConnection."
        def fget(self):
            if self.__response:
                return self.__response.fp
            else:
                return self.__connection.sock
        return locals()
    sock = property(**sock())

    def isResponseReceived(self):
        if self.__response is not None:
            return True
        else:
            return False

    def getResponse(self):
        if self.__response is None:
            self.__response = self.__connection.getresponse()
        else:
            raise Exception("Network error: Response was already received...")
        
    def write(self, data):
        '''
            Writes data and response has not yet been received.
        '''
        if self.__response is not None:
            raise Exception("Network error: Response has already been received...")
        try:
            return self.__connection.send(data)
        except Exception, e:
            raise e

    def getStatus(self):
        '''
            Returns the numeric value of the HTTP response code,
            such as 200, 404, etc.
        '''
        if self.__response is None:
            raise Exception("Network error: Response has not been received yet...")
        return self.__response.status

    def getReason(self):
        '''
            Returns the reason for a failure.
        '''
        if self.__response is None:
            raise Exception("Network error: Response has not been received yet...")
        return self.__response.reason

    def getHeaders(self):
        '''
            Returns the HTTP response headers as a dictionary.
        '''
        if self.__response is None:
            raise Exception("Network error: Response has not been received yet...")
        try:
            if self.__headers is None:
                # The HTTPresponse object can give us a list of tuples of the
                # server's response headers. Let's make a dictionary out of it,
                # for our convenience.
                h = self.__response.getheaders()
                self.__headers = {}
                [ self.__headers.__setitem__(hdr, val) for (hdr, val) in h ]
        except Exception, e:
            print "SnapHttpLib.HttpResponse.getHeaders(): Exception: " + str(e)
            raise e
        return self.__headers

    def read(self, num=None):
        '''
            Reads the specified number of bytes from the server, or (if
            no number of bytes is specified) as much as possible.
        '''
        if self.__response is None:
            raise Exception("Network error: Response has not been received yet...")
        try:
            return self.__response.read(num)
        except Exception, e:
            print "SnapHttpLib.HttpResponse.read(" + str(num) + "): Exception: " + str(e)
            raise e
        
    def close(self):
        '''
            Closes the connection.
        '''
        try:
            if self.__dbg_str is not None:
                print "--- c_" + str(self.__counter) + ". SnapHttpLib.HttpResponse.close (" + str(self.__dbg_str) + ")"
            self.__connection.close()
        except Exception, e:
            print "SnapHttpLib.HttpResponse.close(): Exception: " + str(e)
            raise e
        
        if self.__response is not None:
            try:
                self.__response.close()
            except Exception, e:
                print "SnapHttpLib.HttpResponse.close(): Response Exception: " + str(e)
                raise e


def setUsernamePassword(username, password):
    _HttpAuthenticationHolder._setUsernamePassword(username, password)

def sendreq(method, url, data=None, headers=None, credential=None, timeout=None):
    '''
        Opens a URL. A great deal of flexibility is offered.

            method:     "GET", "POST", "DELETE", PUT"
            url:        The actual, full, URL that we want to reach.
            data:       Any data in message body.
            headers:    Dictionary of HTTP request headers.
            credential: A 2-tuple containing (username, password)
            timeout:    A nonnegative float expressing seconds, or None.

        Returns a HttpResponse object. That object then is used to
        look at the server response and also read data from the
        connection.

        Note that this function here returns without actually having
        requested (read) the initial response from the server. That
        needs to be done by the user of this function by calling the
        getResponse() method on the response object. You can use
        isResponsReceived() on the response to see if that has taken
        place already.
    '''

    (scheme, host, path, params, query, fragment) = urlparse.urlparse(url)
    rempath = urlparse.urlunparse((None, None, path, params, query, None))

    if headers is None:
        headers = {}

    counter = HttpResponse._getNextInstanceCounter()

    if scheme == 'https':
        conn = httplib.HTTPSConnection(host)
    else:
        conn = httplib.HTTPConnection(host)

    # Some debug information before we issue the request. Comment this out in production code...
    # print "++++ c_" + str(counter) + ". SnapHttpLib.HttpResponse.__init__(" + str((method, url, headers)) + ")"

    if credential:
        (uname, passwd) = credential
    else:
        (uname, passwd) = _HttpAuthenticationHolder._getUsernamePassword()
    if (uname is not None)  and  (passwd is not None):
        headers["Authorization"] = "Basic " + base64.encodestring('%s:%s' % (uname, passwd))[:-1]
    conn.request(method.upper(), rempath, data, headers)
    conn.sock.settimeout(timeout)

    # return HttpResponse(False, conn, counter, str((method, url, headers)))
    return HttpResponse(False, conn, counter, None)


def urlopen(method, url, data=None, headers=None, credential=None, timeout=None):
    '''
        Opens a URL. Similar to sendreq(), except that this one tries to
        get the response from the server right away.

            method:     "GET", "POST", "DELETE", PUT"
            url:        The actual, full, URL that we want to reach.
            data:       Any data in message body.
            headers:    Dictionary of HTTP request headers.
            credential: A 2-tuple containing (username, password)
            timeout:    A nonnegative float expressing seconds, or None.

        Returns a HttpResponse object.
    '''
    r = sendreq(method, url, data, headers, credential, timeout)
    r.getResponse()
    return r

