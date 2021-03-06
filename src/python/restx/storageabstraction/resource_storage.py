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
Base class from which all storage abstractions derive.

"""
import restxjson as json

# RESTx imports
from restx.storageabstraction.file_storage import FileStorage
from org.mulesoft.restx.exception        import *

class ResourceStorage(FileStorage):
    """
    Implementation of resource storage methods.

    """

    def loadResourceFromStorage(self, resource_name):
        """
        Load the specified resource from storage.

        @param resource_name:    Name of the selected resource.
        @type resource_name:     string

        @return                  A Python dictionary representation or None
                                 if not found.
        @rtype                   dict

        """
        try:
            buf = self.loadFile(resource_name)
        except RestxFileNotFoundException, e:
            return None
        obj = json.loads(buf)
        return obj

    def deleteResourceFromStorage(self, resource_name):
        """
        Delete the specified resource from storage.

        @param resource_name:    Name of the selected resource.
        @type resource_name:     string

        """
        self.deleteFile(resource_name)

    def listResourcesInStorage(self):
        """
        Return list of resources which we currently have in storage.

        @return:                 List of resource names.
        @rtype:                  list

        """
        try:
            dir_list = self.listFiles()
            return dir_list
        except Exception, e:
            raise RestxException("Problems getting resource list from storage: " + str(e))

    def writeResourceToStorage(self, resource_name, resource_def):
        """
        Store a resource definition.
        
        No return value, but raises RestxException if there is an issue.
        
        @param resource_name: The storage name for this resource
        @type  resource_name: string
        
        @param resource_def: The dictionary containing the resource definition.
        @type  resource_def: dict
        
        @raise RestxException: If the resource cannot be stored.
            
        """
        try:
            buf = json.dumps(resource_def, indent=4)
            self.storeFile(resource_name, buf)
        except Exception, e:
            raise RestxException("Problems storing new resource: " + str(e))

