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
import StringIO
import traceback

# GAE imports
from google.appengine.ext.webapp.util import run_wsgi_app

# RESTx imports
import restx.settings as settings
from restx.httpabstraction.python_http_server import PythonHttpRequest

from restx.logger import *

from restx.httpabstraction.base_server import BaseHttpServer

#
# Note: We are not defining out own Request class here, since we
# can just use the request class used for Python.
#

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
            sys.stderr.write(traceback.format_exc())
            raise e
            """
            #sys.exit(1)        
            """


# ----------------------------------------------------

request_handler = None

def _app_method(environ, start_response):
    global request_handler
    handler = _HttpHandler(request_handler)
    handler.handle(environ, start_response)
    return ""


class GaeHttpServer(BaseHttpServer):
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
        log("Listening for HTTP requests...")
        run_wsgi_app(_app_method)

