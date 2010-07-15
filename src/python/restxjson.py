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


import datetime

from restx.platform_specifics import *

if PLATFORM == PLATFORM_PYTHON:
    from json import *
elif PLATFORM == PLATFORM_GAE:
    from django.utils.simplejson import *
else:
    from simplejson import *

class RestxJsonEncoder(JSONEncoder):
    def __init__(self):
        JSONEncoder.__init__(self, ensure_ascii=False)
    def default(self, obj):
        if isinstance(obj, datetime.datetime)  or isinstance(obj, datetime.date):
            return str(obj)
        return JSONEncoder.default(self, obj)

def restxdumps(obj):
    """
    Encode an object to string, using our own JSON Encoder.

    This method hides the default 'dumps' method that comes with
    the JSON module.

    """
    return RestxJsonEncoder().encode(obj)

