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

# Imports all aspects of the API
from restx.components.api import *

from datetime import datetime, timedelta

# -------------------------------------------------------
# A RESTx component needs to be derived from BaseComponent.
# -------------------------------------------------------
class TimeRange(BaseComponent):

    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "TimeRange"
    DESCRIPTION      = "Allows the selection of time ranges to be sent to other resources."
    DOCUMENTATION    = "Longer description text possibly multiple lines."

    PARAM_DEFINITION = {
                           "base_resource"   :  ParameterDef(PARAM_STRING, "The URI of the resource that accepts time ranges", required=True),
                           "start_time_name" :  ParameterDef(PARAM_STRING, "Name of the parameter for the base resource, which sets the start time", required=True),
                           "end_time_name"   :  ParameterDef(PARAM_STRING, "Name of the parameter for the base resource, which sets the end time", required=True),
                           "count_flag_name" :  ParameterDef(PARAM_STRING, "Name of the flag to get only a log line count", required=False, default=""),
                       }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           # Key into the dictionary is the service name. Has to be an
                           # exact function name.
                           "current_time" : {
                               "desc" : "The current time representation",
                           },
                           "today" : {
                               "desc" : "Today's entries",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL, "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                }
                           },
                           "yesterday" : {
                               "desc" : "Yesterday's entries",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL, "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                }
                           },
                           "last7days" : {
                               "desc" : "Entries over the last 7 days",
                               "params" : {
                                   "count_only" :  ParameterDef(PARAM_BOOL, "If set then we only get the count of lines, not the lines themselves.", required=False, default=False), 
                                }
                           },
                       }

    def __make_time_str(self, dt):
        return dt.strftime("%d/%b/%Y:%H:%M:%S")

    def __make_start_end_params(self, start, end, count_only):
        p = dict()
        p[self.start_time_name] = self.__make_time_str(start)
        p[self.end_time_name]   = self.__make_time_str(end)
        if self.count_flag_name:
            p[self.count_flag_name] = count_only
        return p

    def current_time(self, method, input):
        """
        Return the current time.

        """
        return Result.ok(self.__make_time_str(datetime.now()))

    def today(self, method, input, count_only):
        now   = datetime.now()
        start = datetime(now.year, now.month, now.day, 0, 0, 0)
        status, data = accessResource(self.base_resource, params=self.__make_start_end_params(start, now, count_only))
        return Result(status, data)

    def yesterday(self, method, input, count_only):
        end   = datetime.now()-timedelta(1)
        start = end-timedelta(7)
        status, data = accessResource(self.base_resource, params=self.__make_start_end_params(start, end, count_only))
        return Result(status, data)

    def last7days(self, method, input, count_only):
        now   = datetime.now()
        start = now-timedelta(7)
        status, data = accessResource(self.base_resource, params=self.__make_start_end_params(start, now, count_only))
        return Result(status, data)

       

