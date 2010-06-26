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
Definition of the L{RestxServer} class.

"""

try:
    import json
except:
    import simplejson as json

import httplib
import urlparse

from restxclient.restx_client_exception import RestxClientException
from restxclient.restx_component        import RestxComponent
from restxclient.restx_resource         import RestxResource

class RestxServer(object):
    """
    Used by the client to encapsulate all communication with the server.

    """
    # These are the headers we use for each request
    __DEFAULT_REQ_HEADERS = dict(Accept="application/json")

    # The keys to the server's meta data dictionary.
    __CODE_URI_KEY      = "code"
    __DOC_URI_KEY       = "doc"
    __NAME_KEY          = "name"
    __RESOURCE_URI_KEY  = "resource"
    __STATIC_URI_KEY    = "static"
    __VERSION_KEY       = "version"

    __META_URI          = "/"    # Location of the server's root directory (meta info)

    __server_uri        = None   # Stores the URI of the server to which we connect
    __component_uri     = None   # The URI of where the components can be found
    __doc_uri           = None   # The URI of the server documentation
    __name              = None   # The name of the server
    __resource_uri      = None   # The URI where resources can be found
    __static_uri        = None   # The URI for static content
    __version           = None   # The version string of the server
    __doc               = None   # A cache for the servers's doc string
    __resources         = None   # A cache for the resource-name-plus dictionary
    __components        = None   # A cache for the component-name-plus dictionary

    def _send(self, url, data=None, method=None, status=None, headers=None):
        """
        A sending method that uses our own URL opener.

        Note that we will send all messages with application/json as
        the accept header. JSON is our preferred mode of serializing
        data.

        @param url:     The relative (!) URL on that server to which
                        the request shoudl be sent.
        @type url:      string

        @param data:    Any data object, which will be serialized to
                        JSON if specified.
        @type data:     object

        @param method:  The HTTP request method. Defaults to GET if
                        no data was specified, otherwise POST.
        @type method:   string

        @param status:  Specify the status code that we expect to see.
                        If None, all status codes are allowed. Otherwise
                        the received status code is compared and an
                        exception is thrown if it's not a match.
        @type status:   int

        @param headers: Additional headers that we want to send with the
                        request.
        @type headers:  dict

        @return:        Any data that may have been received from the
                        server.
        @rtype:         string

        """
        if not method:
            # Setting default HTTP method
            if data is None:
                method = "GET"
            else:
                method = "POST"
            
        # Combine default headers with any additional headers
        if not headers:
            headers = self.__DEFAULT_REQ_HEADERS
        else:
            combined_headers = dict()
            combined_headers.update(headers)
            for name, value in self.__DEFAULT_REQ_HEADERS.items():
                combined_headers[name] = value
            headers = combined_headers

        if data:
            headers["Content-length"] = len(data)

        server_conn = httplib.HTTPConnection(self.__host, self.__port)
        server_conn.request(method, url, body=data, headers=headers)

        r = server_conn.getresponse()

        if status is not None:
            if status != r.status:
                r.read()    # Empty the input stream (if we don't do that the next request will be confused)
                raise RestxClientException("Status code %s was expected for request to '%s'. Instead we received %s." % (status, url, r.status))

        data = r.read()
        server_conn.close()
        
        return r.status, data

    def _json_send(self, url, data=None, method=None, status=None):
        """
        Send JSON data to server and assume a JSON reply.

        This is just a wrapper around _send(), which JSON serializes
        the request data and deserializes the return data.

        @param url:     Absolute URL to which the request should be sent.
        @type url:      string

        @param data:    Some object that should be sent.
        @type data:     object

        @param method:  The HTTP request method. Defaults to GET if
                        no data was specified, otherwise POST.
        @type method:   string

        @param status:  Specify the status code that we expect to see.
                        If None, all status codes are allowed. Otherwise
                        the received status code is compared and an
                        exception is thrown if it's not a match.
        @type status:   int

        @return:        Any data that may have been received from the
                        server.
        @rtype:         string

        """
        # If a data object was given then we convert it to JSON.
        if data:
            data = json.dumps(data)

        status, d = self._send(url, data=data, method=method, status=status, headers={"content-Type" : "application/json"})
        return status, json.loads(d)


    # --------------------------------------------
    # Public interface
    # --------------------------------------------

    def __init__(self, server_uri):
        """
        Initialize the server class.

        Send a request for the base meta information to the
        server and remember some of the information that was
        returned.

        It's important to note that the meta information of
        the server is retrieved and cached once. If this
        information should subsequently change, this server
        object won't know about it.

        @param server_uri:      The full URI of the server.
        @type server_uri:       string

        """
        self.__server_uri    = server_uri

        #
        # Need to extract schema, hostname and port from URI
        #
        parse_result = urlparse.urlparse(server_uri)
        if parse_result.scheme != "http":
            raise RestxClientException("Only 'http' schema is currently supported.")
        if parse_result.path  or  parse_result.query:
            raise RestxClientException("No path or query allowed in server URI.")
        if ":" in parse_result.netloc:
            self.__host, port_str = parse_result.netloc.split(":")
            self.__port = int(port_str)
        else:
            self.__host = parse_result.netloc
            self.__port = 80

        #
        # Get meta info from server and perform some sanity checking
        #
        status, d = self._json_send(self.__META_URI, status=200)

        try:
            self.__component_uri = d[self.__CODE_URI_KEY]
            self.__doc_uri       = d[self.__DOC_URI_KEY]
            self.__name          = d[self.__NAME_KEY]
            self.__resource_uri  = d[self.__RESOURCE_URI_KEY]
            self.__static_uri    = d[self.__STATIC_URI_KEY]
            self.__version       = d[self.__VERSION_KEY]
        except KeyError, e:
            raise RestxClientException("Server error: Expected key '%s' missing in server meta data." % str(e))

    def _create_resource(self, uri, rdict):
        """
        Create a new resource.

        Clients should NOT use this method directly. Instead, they
        should use obtain a resource template from a component and
        then call create_resource() on that template.

        @param uri:     Component URI to which this resource description
                        should be posted.
        @type uri:      string

        @param rdict:   The completed dictionary to be posted to
                        this components URI.
        @type rdict:    dict.

        """
        status, data = self._json_send(uri, rdict, status=201)
        return data

    def get_server_uri(self):
        """
        Return the URI of the server to which we are connected.

        @return:        The server's URI.
        @rtype:         string

        """
        return self.__server_uri

    def get_server_version(self):
        """
        Return the version string contained in the server's meta data.

        @return:        The server's version.
        @rtype:         string

        """
        return self.__version

    def get_server_name(self):
        """
        Return the name string contained in the server's meta data.

        @return:        The server's name.
        @rtype:         string

        """
        return self.__name

    def get_server_docs(self):
        """
        Return the doc string for this server.

        Since the doc has its own URI and is potentially longer,
        we are sending an extra request right here, unless the
        information is cached already.

        @return:        The server's doc string.
        @rtype:         string

        """
        if not self.__doc:
            status, self.__doc = self._json_send(self.__doc_uri, status=200)
        return self.__doc

    def get_all_resource_names(self):
        """
        Return the list of all resource names.

        This does not query the meta data for each resource.
        If that is needed, use a separate get_resource()
        call for each resource.

        Alternatively, one may use get_all_resource_names_plus()
        to get at least description string and URI of each
        resource as well.

        The information is cached, thus only the first request
        to get_all_resource_names() or get_all_resource_names_plus()
        results in a request to the server.

        The information is NOT cached since resources can be
        created frequently.

        @return:        List of resource names.
        @rtype:         list

        """
        status, self.__resources = self._json_send(self.__resource_uri, status=200)
        return self.__resources.keys()

    def get_all_resource_names_plus(self):
        """
        Return dictionary with all high-level meta info about all resources.

        This does not query the meta data for each resource.
        If that is needed, use a separate get_resource()
        call for each resource.

        Returns a dictionary keyed by the resource name and
        containing further dictionaries, each containing a 'desc'
        and 'uri' element.

        The information is NOT cached since resources can be
        created frequently.

        @return:        Dictionary with high-level resource info.
        @rtype:         dict

        """
        status, self.__resources = self._json_send(self.__resource_uri, status=200)
        return self.__resources

    def get_all_component_names(self):
        """
        Return the list of all component names.

        This does not query the meta data for each component.
        If that is needed, use a separate get_component()
        call for each component.

        Alternatively, one may use get_all_component_names_plus()
        to get at least description string and URI of each
        component as well.

        The information is cached, thus only the first request
        to get_all_component_names() or get_all_component_names_plus()
        results in a request to the server.

        @return:        List of component names.
        @rtype:         list

        """
        if not self.__components:
            status, self.__components = self._json_send(self.__component_uri, status=200)
        return self.__components.keys()

    def get_all_component_names_plus(self):
        """
        Return dictionary with all high-level meta info about all component.

        This does not query the meta data for each component.
        If that is needed, use a separate get_component()
        call for each component.

        Returns a dictionary keyed by the component name and
        containing further dictionaries, each containing a 'desc'
        and 'uri' element.

        The information is cached.

        @return:        Dictionary with high-level component info.
        @rtype:         dict

        """
        if not self.__components:
            status, self.__components = self._json_send(self.__component_uri, status=200)
        return self.__components

    def get_component(self, name):
        """
        Return a L{RestxComponent} object for the specified component.

        @param name:    Name of component.
        @type name:     string

        @return:        Client representation for the specified component.
        @rtype:         L{RestxComponent}

        """
        status, d = self._json_send(self.__component_uri + "/" + name, status=200)
        return RestxComponent(self, d)

    def get_resource(self, name):
        """
        Return a L{RestxResource} object for the specified resource.

        @param name:    Name of resource.
        @type name:     string

        @return:        Client representation for the specified resource.
        @rtype:         L{RestxResource}

        """
        status, d = self._json_send(self.__resource_uri + "/" + name, status=200)
        return RestxResource(self, d)

    #
    # For convenience, we offer read access to several
    # elements via properties.
    #
    version  = property(get_server_version, None)
    uri      = property(get_server_uri, None)
    name     = property(get_server_name, None)
    docs     = property(get_server_docs, None)

