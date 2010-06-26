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
import restxjson as json
import urllib

# RESTx imports
from restx.components.api import *

class GsearchComponent(BaseComponent):
    NAME             = "GoogleSearchComponent"
    PARAM_DEFINITION = {
                           "api_key" :        ParameterDef(PARAM_STRING, "Google API key", required=True),
                           "default_search" : ParameterDef(PARAM_STRING, "A default search term", required=False,
                                                           default="the current time")
                       }
    
    DESCRIPTION      = "Provides an interface to Google Search."
    DOCUMENTATION    =  """
                        This component is used to perform Google searches.
                        
                        Provide a search term as the 'query' attribute for the
                        'search' sub-resource. If no query is specified then
                        the default search term, specified during resource
                        creation time, is used.
                        """
    SERVICES         = {
                           "search" :   {
                               "desc"   : "Provide 'query' as attribute to GET a search result. A 'num'ber of results can optionally be specified as well.",
                               "params" : {
                                    "query" : ParameterDef(PARAM_STRING, "The search query",
                                                           required=False, default=""),
                                    "num"   : ParameterDef(PARAM_NUMBER, "The number of results you would like to have returned",
                                                           required=False,
                                                           default=10)
                               }
                           }
                       }
    
            
    def search(self, input, method, query, num):
        """
        Perform a Google search.
        
        @param method:     The HTTP request method.
        @type method:      string
        
        @param input:      Any data that came in the body of the request.
        @type input:       string
        
        @return:           The output data of this service.
        @rtype:            string
        
        """
        # This is the official API, which seems to require the API key
        #code, data = self.httpGet("http://base.google.com/base/feeds/snippets?q=%s&key=%s" % (query, key))
        #
        # But we like things in JSON. There is another Google search API, which does things in JSON,
        # and which does not require the API key. It only seems to read 10 (or so) results at any
        # time, so we put this in a loop until we have the requested number of results.
        # 
        start = 1
        results = []
        if not query:
            query=urllib.quote(self.default_search)
        while len(results) < num:
            url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&start=%d" % (query, start)
            code, data_str = self.httpGet(url)
            if code == HTTP.OK:
                try:
                    data      = json.loads(data_str)
                    new_batch = data['responseData']['results']
                    results  += new_batch
                except Exception, e:
                    return HTTP.BAD_REQUEST, "Result data was malformed: " + str(e)
        return Result(code, results[:num])

