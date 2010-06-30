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
The request dispatcher class, which directs requests
to the appropriate browsers.

"""
# RESTx imports
import restx.settings as settings

from org.mulesoft.restx.exception             import *
from org.mulesoft.restx.component.api         import HTTP, Result

from restx.core.basebrowser       import BaseBrowser
from restx.core.staticbrowser     import StaticBrowser
from restx.core.metabrowser       import MetaBrowser
from restx.core.codebrowser       import CodeBrowser 
from restx.core.resourcebrowser   import ResourceBrowser 

BROWSER_MAP   = {
                    settings.PREFIX_META     : MetaBrowser,
                    settings.PREFIX_RESOURCE : ResourceBrowser,
                    settings.PREFIX_CODE     : CodeBrowser,
                    settings.PREFIX_STATIC   : StaticBrowser,
                }
            
class RequestDispatcher(object):
    """
    Takes incoming HTTP requests and sends them off to the
    appropriate modules.
    
    """
    def handle(self, request):
        """
        Handle a request by dispatching it off to the correct handler.
        
        The handler is a 'browser' class, which can be looked up via the
        BROWSER_MAP that is defined in the settings file.
        
        This also catches any RestxExceptions thrown by lower level code and
        translates them into log messages.
        
        @param request:   A properly wrapped request.
        @type request:    RestxHttpRequest
        
        @return:          Response structure and headers
        @rtype:           Tuple of (Result, dict)
        
        """
        content_type = None
        try:
            if request.getRequestPath() == "/":
                browser_class = BROWSER_MAP['/meta']
            else:
                method        = request.getRequestMethod().upper()
                prefix        = "/"+request.getRequestPath().split("/")[1]
                browser_class = BROWSER_MAP.get(prefix)
            
            if browser_class:
                browser_instance = browser_class(request)
                result           = browser_instance.process()
                if result.getStatus() >= 200  and  result.getStatus() < 300:
                    headers = result.getHeaders()
                    # Check if the Content-type return header was set by
                    # the component. If so, we assume that the component
                    # has returned data in the appropriate format already
                    # and we will not perform any encoding.
                    # For example, if an image file is returned then the
                    # component may have set the content type to "image/jpg".
                    if headers:
                        content_type = result.getHeaders().get("Content-type")
                    else:
                        content_type = None
                    if content_type is None:
                        # If all was OK with the request then we will
                        # render the output in the format that was
                        # requested by the client. But only if we don't
                        # have a content-type set on this request already.
                        content_type, data = browser_instance.renderOutput(result.getEntity())
                        result.setEntity(data)
            else:
                result = Result.notFound("Not found" )
        except RestxMethodNotAllowedException, e:
            result = Result(e.code, e.msg)
        except RestxMandatoryParameterMissingException, e:
            result = Result(e.code, e.msg)
        except RestxFileNotFoundException, e:
            result = Result(e.code, e.msg)
        except RestxException, e:
            result = Result.badRequest("Bad request: " + e.msg)

        if content_type:
            result.addHeader("Content-type", content_type);
        
        return result

