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
Allows users and clients to browse the server's installed code.

"""
# Java imports
import restxjson as json

# RESTx imports
import restx.settings as settings

from org.mulesource.restx.exception       import RestxException
from org.mulesource.restx.component.api   import Result

from restx.components       import _CODE_MAP
from restx.resources        import makeResource 
from restx.core.basebrowser import BaseBrowser
from restx.languages        import *

from org.mulesource.restx.util          import Url
from org.mulesource.restx.component.api import HTTP;

EXCLUDE_PREFIXES = [ "_" ]

def getComponentClass(uri):
    """
    Return the specified component class, based on a given URI.
    
    @param uri:     The official URI for this code.
    @type uri:      string
    
    @return         Class of the specified component
                    or None if no matching component class was found.
    @rtype          A class derived from BaseComponent
    
    """
    path_elems = uri[len(settings.PREFIX_CODE):].split("/")[1:]
    component_name  = path_elems[0]   # This should be the name of the code element
    
    # Instantiate the component
    return _CODE_MAP.get(component_name)

def getComponentInstance(uri, resource_name = None):
    """
    Return an instantiated component, the class of which was identified by a URI.

    @param uri:           The official URI for this code.
    @type uri:            string

    @param resource_name: Name of the resource for which the component was instantiated.
    @type resource_name:  string
    
    @return               Instance of the specified component
                          or None if no matching component class was found.
    @rtype                Instance of a class derived from BaseComponent
    
    """
    component_class = getComponentClass(uri)
    if component_class:
        component = component_class()
        component.setResourceName(resource_name)
        return component
    else:
        return None
        
class CodeBrowser(BaseBrowser):
    """
    Handles requests for code info.
    
    """
    def __init__(self, request):
        """
        Initialize the browser with the render-args we need for meta data browsing.
        
        @param request: Handle to the HTTP request that needs to be processed.
        @type request:  RestxHttpRequest
        
        """
        super(CodeBrowser, self).__init__(request,
                                          renderer_args = dict(no_annotations=True,
                                                               no_table_headers=False,
                                                               no_list_indices=False,
                                                               no_borders=False))
    
    def __process_get(self):
        """
        Respond to GET requests.
        
        When someone sends GET requests to the code then
        they want to browse the available code options.
        
        @return:  HTTP return structure.
        @rtype:   Result

        """
        # It's the responsibility of the browser class to provide breadcrumbs
        self.breadcrumbs = [ ("Home", settings.DOCUMENT_ROOT), ("Code", settings.PREFIX_CODE) ]

        if self.request.getRequestPath() == settings.PREFIX_CODE:
            #
            # Just show the home page of the code browser (list of all installed code)
            #
            data = dict([ (name, { "uri" : Url(class_name().getCodeUri()), "desc" : class_name().getDesc() } ) \
                                for (name, class_name) in _CODE_MAP.items() \
                                    if name[0] not in EXCLUDE_PREFIXES ])
        else:
            # Path elements (the known code prefix is stripped off)
            path_elems = self.request.getRequestPath()[len(settings.PREFIX_CODE):].split("/")[1:]
            component_name  = path_elems[0]   # This should be the name of the code element
            
            # Instantiate the component
            component_class = getComponentClass(self.request.getRequestPath())
            if not component_class:
                return Result.notFound("Unknown component")
            component          = component_class()
            component_home_uri = component.getCodeUri()
            self.breadcrumbs.append((component_name, component_home_uri))

            if len(path_elems) == 1:
                #
                # No sub-detail specified: We want meta info about a code segment (component)
                #
                data = component.getMetaData()
                data = languageStructToPython(component, data)
                self.context_header.append(("[ Create resource ]", settings.PREFIX_RESOURCE+"/_createResourceForm/form/"+component_name, "target=_blank"))
            else:
                #
                # Some sub-detail of the requested component was requested
                #
                sub_name = path_elems[1]
                if sub_name == "doc":
                    data       = component.getDocs()
                    self.breadcrumbs.append(("Doc", component_home_uri + "/doc"))
                else:
                    return Result.notFound("Unknown code detail")
                
        return Result.ok(data)
    
    
    def __process_post(self):
        """
        Process a POST request.
        
        The only allowed POST requests to code are requests
        to the base URI of a component. This creates a new resource.
        
        @return:  HTTP return structure.
        @rtype:   Result

        """
        #
        # Start by processing and sanity-checking the request.
        #
        component_class = getComponentClass(self.request.getRequestPath())
        if not component_class:
            return Result.notFound("Unknown component")
        #component = component_class()
        body = self.request.getRequestBody()
        try:
            param_dict = json.loads(body)
        except Exception, e:
            raise RestxException("Malformed request body: " + str(e))
        ret_msg = makeResource(component_class, param_dict)
        return Result.created(ret_msg['uri'], ret_msg)
    
    def process(self):
        """
        Process the request.
        
        @return:  HTTP return structure.
        @rtype:   Result
        
        """
        method = self.request.getRequestMethod()
        if method == HTTP.GET_METHOD:
            return self.__process_get()
        elif method == HTTP.POST_METHOD:
            return self.__process_post()
