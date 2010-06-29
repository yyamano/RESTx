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
Provide an abstraction layer for a concrete HTTP server implementation.

This allows the rest of our code to be written without server specifics
being spread all over the place. That way, we can always change the
concrete HttpServer implementation later on.

"""

#
# By importing RestxHttpRequest, we are exporting this symbol from
# within this module. Gives the users of the abstraction a single
# place from which they get what they need.
#
# The RestxHttpRequest class is an abstract Java class, thus giving us
# a convenient Java and Python interface to the same Python object.
#
from org.mulesoft.restx import RestxHttpRequest


class BaseHttpServer(object):
    """
    Wrapper class around a concrete HTTP server implementation.
    
    """    
    def __init__(self, port, request_handler): pass
