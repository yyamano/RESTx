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

"""
Defines a base class for all components.

"""
# Python imports
import urllib, urllib2, socket

import restx.settings as settings

from restx.storageabstraction.file_storage import FileStorage

from org.mulesoft.restx.component        import BaseComponentCapabilities
from org.mulesoft.restx.component.api    import HttpResult, HTTP


class BaseCapabilities(BaseComponentCapabilities):
    """
    This implements some of the base capabilities, which the framework
    makes available to components of any language. Implemented in Python,
    but by inheriting from a Java interface, it is just as usable from
    within Java.
    
    """
    def __init__(self, component):
        self.__accountname   = None
        self.__password      = None
        self.__my_component  = component

    def getFileStorage(self, namespace=""):
        """
        Return a FileStorage object, which can be used to store data.

        Storage spaces for each resource are separated by resource name,
        this means that two resources cannot share their stored objects,
        even if they are of the same type.

        @param namespace:   A namespace that is used by this resource.
                            Per invocation a resource may chose to create
                            yet another resource namespace under (or within)
                            its inherent namespace.
        @type namespace:    string

        @return:            FileStorage object.

        """
        my_resource_name = self.__my_component.getMyResourceName()
        if my_resource_name:
            if namespace:
                unique_namespace = "%s__%s" % (self.__my_component.getMyResourceName(), namespace)
            else:
                unique_namespace = self.__my_component.getMyResourceName()
            storage = FileStorage(storage_location=settings.STORAGEDB_LOCATION, unique_prefix=unique_namespace)
            return storage
        else:
            # Cannot get storage object when I am not running as a resource
            return None
    
    def __get_http_opener(self, url):
        """
        Return an HTTP handler class, with credentials enabled if specified.
        
        @param url:    URL that needs to be fetched.
        @type url:     string
        
        @return:       HTTP opener (from urllib2)
        
        """
        if self.__accountname  and  self.__password:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, url, self.__accountname, self.__password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
        else:
            opener = urllib2.build_opener()
        return opener
        
    def httpSetCredentials(self, accountname, password):
        """
        The component author can set credentials for sites that require authentication.
        
        @param accountname:    Name of account
        @type accountname:     string
        
        @param password:       Password for account.
        @type password:        string
        
        """
        self.__accountname = accountname
        self.__password    = password
    
    def __http_access(self, url, data=None, headers=None):
        """
        Access an HTTP resource with GET or POST.
        
        @param url:        The URL to access.
        @type url:         string
        
        @param data:       If present specifies the data for a POST request.
        @type data:        Data to be sent or None.
        
        @param headers:    A dictionary of additional HTTP request headers.
        @type headers:     dict
        
        @return:           Code and response data tuple.
        @rtype:            tuple
        
        """
        #
        # For some reason, under Jython we are REALLY slow in handling the kind
        # of host names where we get more than one DNS hit back.
        #
        # As a stop gap measure:
        # 1. Extract the host name from the URI
        # 2. Do a normal DNS lookup for the name, using the socket library
        # 3. Replace the host name in the URI with the IP address string
        # 4. Add a 'Host' header with the original host name to the request
        #
        # Wish I wouldn't have to do that...
        #
        try:
            start_of_hostname = url.index("//")
            host_port, path   = urllib.splithost(url[start_of_hostname:])  # Wants URL starting at '//'
            host, port        = urllib.splitport(host_port)
            ipaddr            = socket.gethostbyname(host)                # One of the possible IP addresses for this host
            url               = url.replace(host, ipaddr, 1)              # Replace only first occurence of host name with IP addr
            add_headers = { "Host" : host }                               # Will add a proper host header
        except Exception, e:
            # Can't parse URI? Just leave it be and let itself sort out.
            add_headers = None
            pass

        opener = self.__get_http_opener(url)
        # Add any custom headers we might have (list of tuples)
        if headers:
            if type(headers) is not type(dict):
                # If this was called from Java then the headers are
                # defined in a HashMap. We need to translate that to
                # a Python dictionary.
                header_dict = dict()
                header_dict.update(headers)
                headers = header_dict

            opener.addheaders.append(headers.items())

        request = urllib2.Request(url)

        if add_headers:
            for name, value in add_headers.items():
                request.add_header(name, value)

        if data:
            request.add_data(data)
        resp = opener.open(request)
        #resp = opener.open(url, data)
        code = HTTP.OK
        data = resp.read()
        return code, data
        
    def httpGet(self, url, headers=None):
        """
        Accesses the specified URL.
        
        If credentials have been specified, they will be used in case
        of HTTP basic authentication.
        
        @param url:        The URL to be accessed.
        @type url:         string
        
        @param headers:    A dictionary of additional HTTP request headers.
        @type headers:     dict
        
        @return:           HttpResult object.
        @rtype:            HttpResult
        
        """
        res                  = HttpResult()
        res.status, res.data = self.__http_access(url, headers=headers)
        return res


    def httpPost(self, url, data, headers=None):
        """
        Send the specified data to the specified URL.
        
        If credentials have been specified, they will be used in case
        of HTTP basic authentication.
        
        @param url:        The URL to be accessed.
        @type url:         string
        
        @param data:       The data to be sent to the URL.
        @type data:        string
        
        @param headers:    A dictionary of additional HTTP request headers.
        @type headers:     dict
        
        @return:           HttpResult object.
        @rtype:            HttpResult
        
        """
        res                  = HttpResult()
        res.status, res.data = self.__http_access(url, data, headers)
        return res

