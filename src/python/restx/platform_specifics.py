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
Platform specific settings for RESTx.

By modifying these, we can switch to a different Http server abstraction
or a different storage abstraction.

"""

import settings

#
# These are the three types of platforms we currently know about.
#
PLATFORM_PYTHON = "Python"
PLATFORM_JYTHON = "Jython"
PLATFORM_GAE    = "GAE"

#
# ------------------------------------------------------------------------------------------
# !!! EDIT THIS:
# ------------------------------------------------------------------------------------------
#
PLATFORM = PLATFORM_JYTHON




#
# Export the correct storage object under the generic name 'STORAGE_OBJECT'
#
if PLATFORM == PLATFORM_GAE:
    from restx.storageabstraction.gae_storage import GaeStorage
    STORAGE_OBJECT = GaeStorage()
else:
    from restx.storageabstraction.resource_storage import ResourceStorage
    STORAGE_OBJECT = ResourceStorage(settings.RESOURCEDB_LOCATION)


#
# Export the correct server class under the generic name 'HttpServer'
#
if PLATFORM == PLATFORM_JYTHON:
    from restx.httpabstraction.jython_java_server import JythonJavaHttpServer as HttpServer
elif PLATFORM == PLATFORM_PYTHON:
    from restx.httpabstraction.python_http_server import PythonHttpServer as HttpServer
else:
    from restx.httpabstraction.gae_http_server import GaeHttpServer as HttpServer


