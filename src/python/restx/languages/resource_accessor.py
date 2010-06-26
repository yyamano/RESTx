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


from restx.resources.resource_runner    import accessResource
from org.mulesource.restx.component.api import HttpResult

from org.mulesource.restx               import ResourceAccessorInterface

class ResourceAccessor(ResourceAccessorInterface):
    """
    This is a helper class that we use to give the Java base component
    access to our accessResource() method.
    
    When a Java component is invoked, it receives an instance
    of this class here, which provides painless access to the
    Python method.
    
    """
    def __init__(self, from_java_conversion_func, to_java_conversion_func):
        """
        Caller provides us with a pre-initialized function to convert
        Java 'dict' objects to Python.
        
        """
        self.from_java_conversion_func = from_java_conversion_func
        self.to_java_conversion_func   = to_java_conversion_func
        
    def accessResourceProxy(self, uri, input, params, method):
        res = HttpResult()
        res.status, res.data = accessResource(uri, input, self.from_java_conversion_func(params), method)
        res.data = self.to_java_conversion_func(res.data)
        return res