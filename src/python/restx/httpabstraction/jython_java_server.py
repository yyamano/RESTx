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

# Java imports
from com.sun.net.httpserver import HttpServer, HttpHandler
from java.net               import InetSocketAddress
from java.lang              import String
from java.io                import InputStreamReader;
from java.io                import BufferedReader
from java.io                import OutputStream
from java.lang              import Exception as JavaException
from java.util.concurrent   import Executors;

# Python imports
import traceback

# RESTx imports
import restx.settings as settings

from restx.logger import *

from restx.httpabstraction.base_server import BaseHttpServer, RestxHttpRequest

class JythonJavaHttpRequest(RestxHttpRequest):
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
    __native_req       = None
    __request_uri_str  = None
    __request_headers  = None
    __response_headers = None

    _native_mode = False

    def __init__(self, *args, **kwargs):
        super(JythonJavaHttpRequest, self).__init__(*args, **kwargs)
        self.__response_headers = dict()
    
    def setNativeMode(self):
        self._native_mode = True

    def setNativeRequest(self, native_req):
        """
        Initialize request wrapper with the native request class.
        
        The RestxHttpRequest may be used anywhere, but is only created within
        the http-abstraction-API. Therefore, it is ok for it to get the
        native-request object passed into it here.
        
        @param native_request:  The request representation of the native server.
        @type native_request:   com.sun.net.httpserver.HttpExchange
        
        """
        self.__native_req = native_req
    
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
        self.__response_body = body if body else ""
        
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
        if self.__native_req:
            return self.__native_req.getProtocol()
        else:
            return None
    
    def getRequestMethod(self):
        """
        Return the method of the request.

        @return:    Method of the request, such as "GET", "POST", etc.
        @rtype:     string
        
        """
        if self.__native_req:
            return self.__native_req.getRequestMethod().upper()
        else:
            return None

    def getRequestURI(self):
        """
        Return the full URI of the request.
        
        @return:    URI of the request, containing server, path
                    and query portion.
        @rtype:     string
        
        """
        if self.__native_req:
            if not self.__request_uri_str:
                self.__request_uri_str = self.__native_req.getRequestURI().toString()
            return self.__request_uri_str
        else:
            return None
    
    def getRequestPath(self):
        """
        Return only the path component of the URI.

        Strip off the DOCUMENT_ROOT, if that is set.
        
        @return:    The path component of the URI.
        @rtype:     string
        
        """
        if self.__native_req:
            path = self.__native_req.getRequestURI().getPath()
            if settings.DOCUMENT_ROOT != ""  and  path.startswith(settings.DOCUMENT_ROOT):
                path = path[len(settings.DOCUMENT_ROOT):]
                if not path:
                    path = "/"
            return path
        else:
            return None
    
    def getRequestHeaders(self):
        """
        Return a dictionary with the request headers.
        
        Each header can have multiple entries, so this is a
        dictionary of lists.
        
        @return:    Dictionary containing a list of values for each header.
        @rtype:     dict
        
        """
        if self.__native_req:
            if not self.__request_headers:
                self.__request_headers = self.__native_req.getRequestHeaders()
            if self._native_mode:
                return self.__request_headers
            else:
                return dict(self.__request_headers)
        else:
            return None
    
    def getRequestQuery(self):
        """
        Return only the query component of the URI.
        
        @return:    Query portion of the URI (the part after the first '?').
        @rtype:     string
        
        """
        if self.__native_req:
            return self.__native_req.getRequestURI().getQuery()
        else:
            return None
    
    def getRequestBody(self):
        """
        Return the body of the request message.
        
        Note that this is not very suitable for streaming or large message bodies
        at this point, since the entire message is read into a single string
        before it is returned to the client.
        
        @return:    Body of the request.
        @rtype:     string
        
        """
        if self.__native_req:
            buffered_reader = BufferedReader(InputStreamReader(self.__native_req.getRequestBody()));
            lines = []
            while True:
                line = buffered_reader.readLine()
                if not line:
                    break
                lines.append(line)
            
            return '\n'.join(lines)
        else:
            return None
    
    def sendResponseHeaders(self):
        """
        Send the previously specified response headers and code.
        
        """
        if self.__native_req:
            response_headers = self.__native_req.getResponseHeaders()
            for name, value in self.__response_headers.items():
                response_headers[name] = [ value ]
            self.__native_req.sendResponseHeaders(self.__response_code, len(self.__response_body))
    
    def sendResponseBody(self):
        """
        Send the previously specified request body.
        
        """
        if self.__native_req:
            os = self.__native_req.getResponseBody()
            if type(self.__response_body) is str or type(self.__response_body) is unicode:
                if self.__response_headers.has_key('Content-type'):
                    (ct, enc) = self.__response_headers['Content-type'].split("charset=")
                else:
                    enc = "US-ASCII"
                os.write(self.__response_body.encode(enc), 0, len(self.__response_body))
            else:
                os.write(self.__response_body, 0, len(self.__response_body))
            os.flush()
            os.close()
        
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
        if self.__native_req:
            self.__native_req.close()  


class __HttpHandler(HttpHandler):
    """
    The native HTTP server (com.sun.net.httpserver.HttpServer) requires a handler class.
    
    Since this is something specific to the particular server,
    this class is not part of the official http-abstraction-API.
    
    """
    def __init__(self, request_handler):
        """
        Initialize the handler class for the native request.
        
        After converting the native request to a RestxHttpRequest,
        this is then passed on to a generic request handler.
        
        @param request_handler: Any class that provides a 'handle()'
                                method that can take a RestxHttpRequest.
                                Those handler classes are provided by
                                or generic code and are passed through
                                to this native handler here during server
                                creation.
        @type request_handler:  Any class that provides a 'handle()' method
                                that can take a RestxHttpRequest. Normally,
                                this is our RequestDispatcher class.
                                
        """
        self.request_handler = request_handler
        
    def handle(self, native_request):
        """
        Handle a native request.
        
        Converts the native request to a RestxHttpRequest, prepares
        logging and exception handling and creates the specific
        handler class.
        
        Any so-far unhandled exceptions are caught here and a stack
        trace is printed to stderr.
        
        @param native_request:    The native request from the native server.
        @type native_request:     com.sun.net.httpserver.HttpExchange
        
        """
        try:
            start_time = datetime.datetime.now()
            req = JythonJavaHttpRequest()
            req.setNativeRequest(native_request)            
            msg = "%s : %s : %s" % (req.getRequestProtocol(),
                                    req.getRequestMethod(),
                                    req.getRequestURI())
            #log(msg, facility=LOGF_ACCESS_LOG)
            result = self.request_handler.handle(req)
            headers = result.getHeaders()
            if headers:
                for name in headers.keySet():
                    req.setResponseHeader(name, headers[name])
            req.setResponse(result.getStatus(), result.getEntity())
            req.sendResponse()
            native_request.close()
            end_time   = datetime.datetime.now()
            td         = end_time-start_time
            request_ms = td.seconds*1000 + td.microseconds//1000
            # This is something to improve: Sometimes we may get binary
            # data, which can't be converted to a string. In that case,
            # we should find other means to determine the size of the data.
            try:
                l = len(str(result.getEntity()))
            except:
                l = -1
            log("%s : %sms : %s : %s" % (msg, request_ms, result.getStatus(), l),
                                         start_time = start_time, facility=LOGF_ACCESS_LOG)
        except Exception, e:
            print traceback.format_exc()
            sys.exit(1)
        except JavaException, e:
            print "JAVA exception: ", e.printStackTrace()


class JythonJavaHttpServer(BaseHttpServer):
    """
    Wrapper class around a concrete HTTP server implementation.
    
    """
            
    __native_server = None
    
    def __init__(self, port, request_handler):
        """
        Initialize and start an HTTP server.
        
        Uses a native HTTP server implementation, in this case
        the com.sun.net.httpserver.HttpServer.
        
        @param port:            The port on which the server should listen.
        @type port:             int
        
        @param request_handler: The request handler class from our generic code.
        @type request_handler:  Any class with a 'handle()' method that can take a
                                RestxHttpRequest. In our case, this is normally the
                                RequestDispatcher class.
        
        """
        self.request_handler = request_handler
        self.__native_server = HttpServer.create(InetSocketAddress(port), 5)
        self.__native_server.createContext(settings.DOCUMENT_ROOT if settings.DOCUMENT_ROOT != "" else "/", __HttpHandler(request_handler))
        self.__native_server.setExecutor(Executors.newCachedThreadPool())
        self.__native_server.start()
        log("Listening for HTTP requests on port %d..." % port)
