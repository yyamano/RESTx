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
Definition of the RestxClient API.

Exports all you need to work with the RESTx client API.

Makes available the following classes:

    - L{RestxClientException}
    - L{RestxServer}
    - L{RestxComponent}
    - L{RestxParameter}
    - L{RestxService}
    - L{RestxAccessibleService}
    - L{RestxResource}
    - L{RestxResourceTemplate}

Important: None of these objects should be created directly
by the client, except the L{RestxServer} object. All other
objects are created for you by various methods on those
objects.

Therefore, in the documentation of this package, the only
__init__() method of interest to the client developer is the
one in the L{RestxServer} class.

"""
from restxclient.restx_client_exception import *
from restxclient.restx_component        import RestxComponent
from restxclient.restx_parameter        import RestxParameter
from restxclient.restx_server           import RestxServer
from restxclient.restx_service          import RestxService
from restxclient.restx_service          import RestxAccessibleService
from restxclient.restx_resource         import RestxResource
from restxclient.restx_resourcetemplate import RestxResourceTemplate


