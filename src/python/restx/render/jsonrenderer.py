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
Outputs JSON representation of data.
 
"""

# Python imports
import restxjson as json

# RESTx imports
from restx.render.baserenderer import BaseRenderer

from restx.platform_specifics  import *

from org.mulesoft.restx.util import Url


def _default(obj):
    """
    Take a non-standard data type and return its string representation.
    
    This function is given to simplejson as a fall back for any types
    that it doesn't know how to render.
    
    @param obj:    A non-standard object to be rendered for JSON.
    @type  obj:    object
    
    @return:       String representation suitable for JSON.
    
    """
    return str(obj)

def _recursive_type_fixer(obj):
    """
    Convert unusual types to strings in recursive structures.

    Under GAE we cannot specify a default for the JSON encoder,
    which is very annoying. So this method is only called when
    we are running under GAE. It traverses the entire data structure
    and converts the types specified in FIX_TYPES to strings.

    """
    FIX_TYPES = [ Url ]
    if type(obj) in FIX_TYPES:
        return str(obj)
    if type(obj) is list:
        new_list = []
        for e in obj:
            new_list.append(_recursive_type_fixer(e))
        return new_list
    if type(obj) is dict:
        new_dict = {}
        for k, v in obj.items():
            if type(k) in FIX_TYPES:
                k = str(k)
            if type(v) in FIX_TYPES:
                v = str(v)
            else:
                v = _recursive_type_fixer(v)
            new_dict[k] = v
        return new_dict
    return obj
        

class JsonRenderer(BaseRenderer):
    """
    Class to render data as JSON.
        
    """
    CONTENT_TYPE = "application/json; charset=UTF-8"

    def render(self, data, top_level=False):
        """
        Render the provided data for output.
        
        @param data:        An object containing the data to be rendered.
        @param data:        object
        
        @param top_level:   Flag indicating whether this we are at the
                            top level for output (this function is called
                            recursively and therefore may not always find
                            itself at the top level). This is important for
                            some renderers, since they can insert any framing
                            elements that might be required at the top level.
                            However, for the JSON renderer this is just
                            ignored.
        @param top_level:   boolean
        
        @return:            Output buffer with completed representation.
        @rtype:             string
        
        """
        # simplejson can only handle some of the base Python datatypes.
        # Since we also have other types in the output dictionaries (URIs
        # for example), we need to provide a 'default' method, which
        # simplejson calls in case it doesn't know what to do.

        # Need to use our newly defined Url encoder, since otherwise
        # json wouldn't know how to encode a URL
        if PLATFORM == PLATFORM_GAE:
            # That doesn't seem to be supported when running in
            # GAE, though. So, in that case we first perform a very
            # manual fixup of the object, replacing all occurrances
            # of unusual types with their string representations.
            data = _recursive_type_fixer(data)
            out = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
        else:
            out = json.dumps(data, ensure_ascii=False, default=_default, sort_keys=True, indent=4)

        return out

