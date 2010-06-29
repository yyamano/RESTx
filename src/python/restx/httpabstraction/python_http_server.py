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
Provide an abstraction layer for a concrete HTTP server implementation.

This allows the rest of our code to be written without server specifics
being spread all over the place. That way, we can always change the
concrete HttpServer implementation later on.

"""

# Python imports
import sys
import httplib
import StringIO
import traceback

# RESTx imports
import restx.settings as settings

from restx.logger import *

from restx.httpabstraction.base_server import BaseHttpServer, RestxHttpRequest

from org.mulesoft.restx.component.api import HTTP

from restx.platform_specifics import *
if PLATFORM == PLATFORM_PYTHON:
    from paste import httpserver

class PythonHttpRequest(RestxHttpRequest):
    """
    Wrapper class around a concrete HTTP request representation.
    
    The class contains information about the received request and
    also provided the means to send a response. Therefore, this
    class encapsulates and controls the entire HTTP exchange between
    client and server.
    
    This class is part of the official http-abstraction-API. It is
    intended to be used by the rest of the code, shielding it from
    the specific server implementation.
    
    """
    __response_code    = None
    __request_headers  = None
    __response_headers = dict()
    
    def __init__(self, environ, start_response):
        """
        Initialize request wrapper with the native request class.
        
        """
        self.environ        = environ
        self.start_response = start_response
    
    def setResponseCode(self, code):
        """
        Set the response code, such as 200, 404, etc.
        
        This is the code that is sent in the response from the server
        to the client.
                
        The method can be called multiple times with different values
        before any of the send methods are called.
        
        @param code:  HTTP response code
        @type code:   int
        
        """
        self.__response_code = code
        
    def setResponseBody(self, body):
        """
        Set the response body.
        
        This method may be called multiple times with different values.
        
        @param body:    The data that should be send in the response body.
        @type body:     string
        
        """
        self.__response_body = body

    def setResponseHeader(self, name, value):
        """
        Set a header for this response.

        @param name:    Name of the header.
        @type name:     string

        @param value:   Value for the header.
        @type value:    string

        """
        self.__response_headers[name] = value

    def setResponse(self, code, body):
        """
        Set response code and body in one function.

        Same as calling setResponseCode() and setResponseBody()
        separately.
        
        @param code:    HTTP response code
        @type code:     int

        @param body:    The data that should be send in the response body.
        @type body:     string
        
        """
        self.setResponseCode(code)
        self.setResponseBody(body)

    def getRequestProtocol(self):
        """
        Return the protocol of the request.
        
        @return:    Protocol of the request, such as "HTTP/1.1"
        @rtype:     string
        
        """
        return self.environ['SERVER_PROTOCOL']
 
    def getRequestMethod(self):
        """
        Return the method of the request.

        @return:    Method of the request, such as "GET", "POST", etc.
        @rtype:     string
        
        """
        return self.environ['REQUEST_METHOD']

    def getRequestURI(self):
        """
        Return the full URI of the request.
        
        @return:    URI of the request, containing server, path
                    and query portion.
        @rtype:     string
        
        """
        uri = self.environ['PATH_INFO']
        if self.environ['QUERY_STRING']:
            uri += "?%s" % self.environ['QUERY_STRING']
        return uri
    
    def getRequestPath(self):
        """
        Return only the path component of the URI.
        
        @return:    The path component of the URI.
        @rtype:     string
        
        """
        return self.environ['PATH_INFO']
    
    def getRequestHeaders(self):
        """
        Return a dictionary with the request headers.
        
        Each header can have multiple entries, so this is a
        dictionary of lists.
        
        @return:    Dictionary containing a list of values for each header.
        @rtype:     dict
        
        """
        if not self.__request_headers:
            self.__request_headers = dict()
            if 'HTTP_ACCEPT' in self.environ:
                self.__request_headers['Accept'] = self.environ['HTTP_ACCEPT'].split(";")
            if 'CONTENT_TYPE' in self.environ:
                self.__request_headers['Content-type'] = self.environ['CONTENT_TYPE'].split(";")
        return self.__request_headers
    
    def getRequestQuery(self):
        """
        Return only the query component of the URI.
        
        @return:    Query portion of the URI (the part after the first '?').
        @rtype:     string
        
        """
        query = self.environ['QUERY_STRING']
        return query
    
    def getRequestBody(self):
        """
        Return the body of the request message.
        
        Note that this is not very suitable for streaming or large message bodies
        at this point, since the entire message is read into a single string
        before it is returned to the client.
        
        @return:    Body of the request.
        @rtype:     string
        
        """
        #buffered_reader = BufferedReader(InputStreamReader(self.__native_req.getRequestBody()));
        if self.getRequestMethod() in [ HTTP.POST_METHOD, HTTP.PUT_METHOD ]:
            fp = self.environ['wsgi.input']
            lines = []
            while True:
                line = fp.readline()
                if not line:
                    break
                lines.append(line)
            return '\n'.join(lines)
        else:
            return ""
    
    def sendResponseHeaders(self):
        """
        Send the previously specified response headers and code.
        
        """
        
        self.write_callable = self.start_response('%d %s' % (self.__response_code, httplib.responses[self.__response_code]),
                                                   self.__response_headers.items())
    
    def sendResponseBody(self):
        """
        Send the previously specified request body.
        
        """
        if not self.__response_body:
            self.__response_body = ""
        self.write_callable(self.__response_body)
        
    def sendResponse(self):
        """
        Send the previously specified response headers, code and body.
        
        This is the same as calling sendResponseHeaders() and sendResponseBody()
        separately.
        
        """
        self.sendResponseHeaders()
        self.sendResponseBody()
        
    def close(self):
        """
        Close this connection.
        
        """
        pass


class _HttpHandler(object):
    """
    Since this is something specific to the particular server,
    this class is not part of the official http-abstraction-API.
    
    """
    def __init__(self, request_handler):
        self.request_handler = request_handler
        
    def handle(self, environ, start_response):
        try:
            start_time = datetime.datetime.now()
            req = PythonHttpRequest(environ, start_response)            
            msg = "%s : %s : %s" % (req.getRequestProtocol(),
                                    req.getRequestMethod(),
                                    req.getRequestURI())
            #log(msg, facility=LOGF_ACCESS_LOG)
            code, response_body, headers = self.request_handler.handle(req)
            for name, value in headers.items():
                req.setResponseHeader(name, value)
            req.setResponse(code, response_body)
            req.sendResponse()
            req.close()
            end_time   = datetime.datetime.now()
            td         = end_time-start_time
            request_ms = td.seconds*1000 + td.microseconds//1000
            log("%s : %sms : %s : %s" % (msg, request_ms, code, len(response_body)),
                start_time = start_time, facility=LOGF_ACCESS_LOG)
        except Exception, e:
            print traceback.format_exc()
            sys.exit(1)        


# ----------------------------------------------------

request_handler = None

def _app_method(environ, start_response):
    global request_handler
    handler = _HttpHandler(request_handler)
    handler.handle(environ, start_response)
    return ""


class PythonHttpServer(BaseHttpServer):
    """
    Wrapper class around a concrete HTTP server implementation.
    
    """
            
    __native_server = None
    
    def __init__(self, port, req_handler):
        """
        Initialize and start an HTTP server.
        
        Uses the built-in simple HTTP server implementation that
        comes with Python.
        
        @param port:            The port on which the server should listen.
        @type port:             int
        
        @param request_handler: The request handler class from our generic code.
        @type request_handler:  Any class with a 'handle()' method that can take a
                                RestxHttpRequest. In our case, this is normally the
                                RequestDispatcher class.
        
        """
        global request_handler
        request_handler = req_handler
        log("Listening for HTTP requests on port %d..." % port)
        httpserver.serve(_app_method, host="0.0.0.0", port=port)

