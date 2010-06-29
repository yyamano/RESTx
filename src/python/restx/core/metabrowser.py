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
Allows users and clients to browse the server's meta information.

"""
import restx.settings as settings

from restx.core.basebrowser import BaseBrowser

from org.mulesoft.restx.util          import Url
from org.mulesoft.restx.component.api import HTTP, Result

        
class MetaBrowser(BaseBrowser):
    """
    Handles requests for meta data of the server.
    
    Meta data here is defined as non-code and non-resource data.
    For example, the name of the server, version number, links to
    the other, more interesting sections, etc.
    
    Just contains a bunch of static links.
    
    """
    def __init__(self, request):
        """
        Create the new meta browser for a request.
        
        @param request:  The client's HTTP request.
        @type request:   RestxHttpRequest
        
        """
        # Initialize the browser with the render-args we need for meta data browsing
        super(MetaBrowser, self).__init__(request,
                                          renderer_args = dict(no_annotations=True,
                                                               no_list_indices=True,
                                                               no_borders=False))
    def process(self):
        """
        Process the request.
        
        Produce the data that needs to be displayed for any request
        handled by this browser. Currently, there is only one request
        handled by the meta browser.
        
        @return:  Http return structure.
        @rtype:   Result
        
        """
        self.breadcrumbs = [ ("Home","/") ]

        path = self.request.getRequestPath()
        if path in [ "/", settings.PREFIX_META ]:
            data = {
                    "code"     : Url(settings.PREFIX_CODE),
                    "resource" : Url(settings.PREFIX_RESOURCE),
                    "static"   : Url(settings.PREFIX_STATIC),
                    "name"     : "MuleSoft RESTx server",
                    "version"  : settings.get_version(),
                    "doc"      : Url(settings.PREFIX_META + "/doc")
            }
            result = Result.ok(data)
            
        elif path == settings.PREFIX_META + "/doc":
            self.breadcrumbs.append(("Doc", settings.PREFIX_META + "/doc"))
            result = Result.ok(settings.get_docs())
        else:
            result = Result.notFound("Don't know this meta page")
        
        return result
