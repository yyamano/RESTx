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

# RESTx imports
from restx.components.api import *

class TwitterComponent(BaseComponent):
    NAME             = "TwitterComponent"
    PARAM_DEFINITION = {
                         "account_name" :     ParameterDef(PARAM_STRING,   "Twitter account name"),
                         "account_password" : ParameterDef(PARAM_PASSWORD, "Password")
                       }
    
    DESCRIPTION      = "Provides access to a Twitter account."
    DOCUMENTATION    =  \
"""The Twitter component is designed to provide access to a Twitter account.


It can be used to get as well as update status, or to view the timeline of
a Twitter account.


To create the resource, the Twitter account name and password need to be specified.
"""
    SERVICES         = {
                         "status" :   { "desc" : "You can GET the status or POST a new status to it." },
                         "timeline" : { "desc" : "You can GET the timeline of the user." },
                       }
    

    def __get_status(self, accountname):
        """
        Get a the latest twitter status for the specified account.
        
        @param accountname: Name of the account for which we get the status.
        @type accountname:  string
        
        @return:            The status text.
        @rtype:             string
        
        """
        # Get the status for this account from Twitter (we get it in JSON format)
        code, data = self.httpGet("http://api.twitter.com/1/users/show.json?screen_name=%s" % accountname)
        if code == HTTP.OK:
            obj = json.loads(data)
        else:
            return "Problem with Twitter: " + data
        
        # Return the requested information, in this case the latest status
        return obj['status']['text']
    
    def __post_status(self, accountname, password, input):
        """
        Post a the new twitter status for the specified account.
        
        @param accountname: Name of the account for which we post the status.
        @type accountname:  string
        
        @param password:    The password for this account.
        @type password:     string
        
        @param input:       The new status update text.
        @type input:        string

        @return:            The status text.
        @rtype:             string
        
        """
        # Send a new status string to the Twitter account
        self.httpSetCredentials(accountname, password)
        code, data = self.httpPost("http://api.twitter.com/1/statuses/update.xml",
                                   "status=%s" % input)
        data = "Status updated"

        # Return the requested information, in this case the latest status
        return data
            
    def status(self, method, input):
        """
        Gets or updates the twitter status for the specified account.
        
        @param method:     The HTTP request method.
        @type method:      string
        
        @param input:      Any data that came in the body of the request.
        @type input:       string
        
        @return:           The output data of this service.
        @rtype:            string
        
        """
        # Get my parameters
        if method == HTTP.GET:
            return Result.ok(self.__get_status(self.account_name))
        else:
            return Result.ok(self.__post_status(self.account_name, self.account_password, input))

    def timeline(self, method, input):
        """
        Get the user's timeline.
        
        @param request:    Information about the HTTP request.
        @type request:     RestxHttpRequest
        
        @param input:      Any data that came in the body of the request.
        @type input:       string
        
        @param params:     Dictionary of parameter values.
        @type params:      dict
        
        @param method:     The HTTP request method.
        @type method:      string
        
        @return:           The output data of this service.
        @rtype:            string

        """
        # Get my parameters
        self.httpSetCredentials(self.account_name, self.account_password)
        code, obj_str = self.httpGet("http://api.twitter.com/1/statuses/user_timeline.json")
        if code == HTTP.OK:
            obj = json.loads(obj_str)
        else:
            obj = obj_str
        return Result.ok(obj)

