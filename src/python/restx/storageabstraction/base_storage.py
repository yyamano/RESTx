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

class BaseStorage(object):
    """
    Abstract implementation of the base storage methods.

    """
    def loadFile(self, file_name):
        """
        Load the specified file from storage.

        @param file_name:    Name of the selected file.
        @type file_name:     string

        @return              Buffer containing the file contents.
        @rtype               string

        """
        pass

    def storeFile(self, file_name, data):
        """
        Store the specified file in storage.

        @param file_name:    Name of the file.
        @type file_name:     string

        @param data:         Buffer containing the file contents.
        @type data:          string

        """
        pass

    def deleteFile(self, file_name):
        """
        Delete the specified file from storage.

        @param file_name:    Name of the selected file.
        @type file_name:     string

        """
        pass

    def listFiles(self):
        """
        Return list of all files in the storage.

        @return:                 List of file names.
        @rtype:                  list

        """
        pass

    def loadResourceFromStorage(self, resource_name):
        """
        Load the specified resource from storage.

        @param resource_name:    Name of the selected resource.
        @type resource_name:     string

        @return                  Buffer containing the resource definition
                                 as a JSON string or None if not found.
        @rtype                   string

        """
        pass

    def deleteResourceFromStorage(self, resource_name):
        """
        Delete the specified resource from storage.

        @param resource_name:    Name of the selected resource.
        @type resource_name:     string

        """
        pass

    def listResourcesInStorage(self):
        """
        Return list of resources which we currently have in storage.

        @return:                 List of resource names.
        @rtype:                  list

        """
        pass

    def writeResourceToStorage(self, resource_name, resource_def):
        """
        Store a resource definition.
        
        No return value, but raises RestxException if there is an issue.
        
        @param resource_name: The storage name for this resource
        @type  resource_name: string
        
        @param resource_def: The dictionary containing the resource definition.
        @type  resource_def: string
        
        @raise RestxException: If the resource cannot be stored.
            
        """
        pass

