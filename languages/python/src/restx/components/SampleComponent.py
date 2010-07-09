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
A sample template for RESTx components, written in Python.

"""
# Imports all aspects of the API
from restx.components.api import *

# -------------------------------------------------------
# A RESTx component needs to be derived from BaseComponent.
# -------------------------------------------------------
class SampleComponent(BaseComponent):

    # -----------------------------------------------
    # Tell RESTx some information about this component.
    #
    # The following are well-known names that RESTx
    # is looking for when dealing with a component.
    # -----------------------------------------------

    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "SampleComponent"
    DESCRIPTION      = "One line description of the component"
    DOCUMENTATION    = "Longer description text possibly multiple lines."

    # Resource creation time parameters.
    # Each parameter is created through a ParameterDef object, which encapsulates
    # the definition of the parameter. The PARAM_* argument determines the type
    # of the parameter. Currently, we know PARAM_STRING, PARAM_NUMBER and PARAM_BOOL.
    PARAM_DEFINITION = {
                           # With 'required' flag set, this parameter is mandatory. No default
                           # value needs to be specified.
                           "some_parameter" :    ParameterDef(PARAM_STRING, "Short description of this parameter",
                                                              required=True),
                           # With 'required' flag not set, the parameter is optional. A default value
                           # must then be provided.
                           "another_parameter" : ParameterDef(PARAM_NUMBER, "Short description of this parameter",
                                                              required=False, default=123.4)
                       }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           # Key into the dictionary is the service name. Has to be an
                           # exact function name.
                           "some_subresource" : {
                               # A human readable, brief description of the service.
                               "desc" : "This is the XYZ subresource",
                               # Definition of all parameters that this service accepts and which
                               # therefore are exposed on the URI command line. Can be skipped if
                               # the service does not take parameters.
                               "params" : {
                                   # Names of these parameters need to match the names of the
                                   # service method.
                                   "text" : ParameterDef(PARAM_STRING, "This is a text parameter",
                                                         required=True),   # is required, so no default needed
                                   "num"  : ParameterDef(PARAM_NUMBER, "A numeric parameter",
                                                         required=False,   # not required, so a default is needed
                                                         default=10)
                               },
                               # Define the list of positional parameters in their desired order
                               # Note that positional parameters may either be set with query-type
                               # arguments on the URI command line, or as path elements in the URI.
                               "positional_params": [ "num" ]
                           }
                       }
        

    def some_subresource(self,
               method, input,    # These two parameters always need to be present
               text, num):       # These are the additional parameters for this service, specified above
        """
        The method that provides the XYZ subresource.
        
        @param method:     The HTTP request method.
        @type method:      string
        
        @param input:      Any data that came in the body of the request.
        @type input:       string

        @param text:       A text parameter.
        @type text:        string

        @param num:        A numerical parameter.
        @type num:         number
        
        @return:           The output data of this service.
        @rtype:            Result

        """
        # -------------------------------------------------
        # Any kind of processing may take place here.
        # No restriction on the available language features
        # and accessible libraries.

        # -----------------------------------------------
        # Resource-creation time parameters are available
        # as normal attributes of this object. For example,
        # you could write:
        #
        # self.some_parameter
        # self.another_parameter
        
        # -----------------------------------------------
        # BaseComponent provides a few facilities to make
        # life easier for the component author.
        #
        # Specifically:
        #
        # HTTP access:
        #     self.httpGet()
        #     self.httpPost()
        #     self.setCredentials()
        #
        # Storage:
        #     self.getFileStorage() (providing: loadFile(), storeFile(), deleteFile(), listFiles())
        #
        # Accessing other resources:
        #     accessResource()

        # -------------------------------------------------------------------------
        # Preparing return data:
        #     Result object, with convenient factory methods.
        #
        # Return data can be objects of the following types: Strings, boolean,
        # numbers, dicts or lists. Dicts or lists may contain elements
        # of any of these types, including further dicts or lists. Thus,
        # it is possible to assemble lists or complex, hirarchical data structures
        # as return values.
  
        return Result.ok(data)

