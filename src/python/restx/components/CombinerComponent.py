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
A test component.

"""
# Python imports
import urllib

# RESTx imports
from restx.components.api                 import *
#from restx.components                     import GsearchComponent

class CombinerComponent(BaseComponent):
    NAME             = "CombinerComponent"
    PARAM_DEFINITION = {
                           "some_number" :     ParameterDef(PARAM_NUMBER,   "Some number", required=True),
                           "some_boolean" :    ParameterDef(PARAM_BOOL,     "Some flag", required=True),
                       }
    
    DESCRIPTION      = "Calls another component."
    DOCUMENTATION    =  """
                        This is just a test to see how we can call another component.
                        
                        """
    SERVICES         = {
                           "combine" :   {
                               "desc"   : "Combines stuff"
                           },
                           "combined_results" :   {
                               "desc"   : "Combines stuff"
                           }
                       }
    
            
    def combine(self, method, input):
        """
        Calls another component.
        
        @param method:     The HTTP request method.
        @type method:      string
        
        @param input:      Any data that came in the body of the request.
        @type input:       string
        
        @return:           The output data of this service.
        @rtype:            string
        
        """
        # If you want to use another resource from within your component
        # code you can do this in three different ways:
        #
        #   1. Issue an HTTP request to the resource's URI. Works
        #      but is not as efficient as it could be if you are
        #      already running in the same process as that other resource.
        #
        #   2. Instantiate the component and provide all the necessary
        #      arguments yourself.
        #
        #   3. Use the accessResource() method to utilizse an already
        #      existing resource definition. This is nice, because
        #      you only need to provide the run-time parameters, if any.
        #
        
        #
        # Example of (2): Instantiating the component directly.
        #
        #gsearch_component = GsearchComponent()
        #code, data = gsearch_component.search(None, None, { 'query'   : 'mule+esb',
        #                                               'api_key' : "ABQIAAAApvtgUnVbhZ4o1RA5ncDnZhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxS5mUUQ41lAGdMeNzzWizhSGRxfiA" })
        #
        # Example of (3): Using an already existing resource definition.
        #
        #code, data = accessResource("/resource/MyGoogleSearch/search", params = { "query" : "mule+esb" })
        code, data = accessResource("/resource/MyJavaTestComponent/foobar",
                                    params = { "query" : "mule+esb", "num" : 1123 })
        
        if code == HTTP.OK:
            result = Result.ok(data)
        else:
            result = Result(code, "Looks like there was a problem: " + str(data))
        return result



    def combined_results(self, method, input):
        return Result.ok("foo")
        code, pr_contacts    = accessResource("/resource/PR_contacts/for_websites")
        code, search_results = accessResource("/resource/AboutUs/search", params={"num":"50"})

        result = list()
        for res in search_results:
            if res['visibleUrl'] in pr_contacts:
                result.append({
                     "url"         : res['url'],
                     "content"     : res['content'],
                     "pr_contacts" : {
                        "site"    : res['visibleUrl'],
                        "contact" : pr_contacts[res['visibleUrl']]
                    }
               })
        return Result.ok(result)

