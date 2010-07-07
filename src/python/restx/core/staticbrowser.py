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
Serves static files.

"""
import array

import restx.settings as settings

from restx.core.basebrowser import BaseBrowser

from org.mulesoft.restx.component.api import HTTP, Result
from org.mulesoft.restx.util import RawFileReader

from java.io import File
from java.io import FileInputStream
from java.nio import ByteBuffer
from java.lang import Exception as JavaException


        
class StaticBrowser(BaseBrowser):
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
        super(StaticBrowser, self).__init__(request,
                                            renderer_args = dict(raw=True))

    def process(self):
        """
        Process the request.
        
        Produce the data that needs to be displayed for any request
        handled by this browser. Currently, there is only one request
        handled by the meta browser.
        
        @return:  Http return code and data as a tuple.
        @rtype:   tuple
        
        """
        path = self.request.getRequestPath()[len(settings.PREFIX_STATIC)+1:]
        if ".." in path:
            # Won't allow that
            return HTTP.BAD_REQUEST, "Invalid path specifier"
        if path.endswith("/"):
            path = path[:-1]
            
        try:
            fname = settings.get_root_dir()+settings.STATIC_LOCATION + path
            rfr   = RawFileReader()
            data  = rfr.readFile(fname)
            res   = Result.ok(data)
            # Examine the extension of the filename to see if we can set the content
            # type based on any of them. If we set the content type here then the
            # request dispatcher will not attempt to call a render method on the
            # data we return.
            i = path.rfind(".")
            if i > -1:
                # Found an extension in the filename
                ext = path[i+1:].lower()
                if ext in [ "jpg", "png", "gif", "jpeg" ]:
                    res.addHeader("Content-type", "image/%s" % ext)
            return res
        except (Exception, JavaException), e:
            return Result.notFound("Not found")
            
