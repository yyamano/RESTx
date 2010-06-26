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
Base class for all content browser classes.

"""
# RESTx imports
import restx.settings as settings

from restx.render import HtmlRenderer
from restx.render import JsonRenderer

from org.mulesource.restx.component.api import HTTP, Result

class BaseBrowser(object):
    """
    A browser is a class that handles specific requests after they
    are assigned by the request-dispatcher.
    
    For example, there might be a specialized browser to deal with
    the installed components/code, another browser for server meta data
    and another to deal with resources.
    
    The RequestDispatcher instantiates specific browsers based on
    the URI prefix.
    
    This base class provides methods to detect the requested content
    type and to format output according to that content type.
    
    """
    def __init__(self, request, renderer_args = None):
        """
        Initialize and perform analysis of request headers.
        
        The 'human_client' flag is set unless 'application/json'
        was requested in the accept header. This is because we
        are assuming that a non-human client wants the easily
        parsable json.
                        
        @param request:        This HTTP request.
        @type request:         RestxHttpRequest
        
        @param renderer_args:  A dictionary of arguments for the
                               chosen renderer. It's passed straight through
                               to the renderer and is not used by the browser.
        @type renderer_args:   dict (or None)
        
        """
        self.request        = request
        self.headers        = request.getRequestHeaders()
        accept_header       = self.headers.get("Accept")
        if not accept_header:
            accept_header = list()
        self.human_client   = False if "application/json" in accept_header or settings.NEVER_HUMAN else True
        self.header         = ""
        self.footer         = ""
        self.renderer_args  = renderer_args
        self.breadcrumbs    = list()
        self.context_header = list()  # Contextual menus or other header items, possibly displayed by renderer
    
    def renderOutput(self, data):
        """
        Take a Python object and return it rendered.
        
        This uses a specific renderer class to convert the raw
        data (a Python object) to data that can be sent back to
        the client.
        
        @param data:  A Python object that should consist only of dictionaries
                      and lists. The output is rendered in JSON, HTML, etc.
                      based on details we have gleaned from the request. For
                      example, there is a human_client flag, which if set indicates
                      that the output should be in HTML.
        @type data:   object
        
        @return:      Tuple with content type and rendered data, ready to be sent to the client.
        @rtype:       tuple of (string, string)

        """
        if self.human_client:
            renderer = HtmlRenderer(self.renderer_args, self.breadcrumbs, self.context_header)
        else:
            renderer = JsonRenderer(self.renderer_args)
        return renderer.CONTENT_TYPE, renderer.base_renderer(data, top_level=True)
    
    def process(self):
        """
        Process the request.
        
        This needs to be overwritten with a specific implementation.
        
        @return:  Http return code and data as a tuple.
        @rtype:   tuple
        
        """
        return Result.ok("Base Browser")

                
