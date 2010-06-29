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

# Python imports
import os

# RESTx imports
import restx.settings as settings
from org.mulesoft.restx.exception     import *
from org.mulesoft.restx.component.api import FileStore

class FileStorage(FileStore):
    """
    Abstract implementation of the base storage methods.

    """
    def __init__(self, storage_location, unique_prefix=""):
        """
        The unique prefix is used to create a namespace in a flat bucket.

        """
        self.storage_location = storage_location
        self.unique_prefix    = unique_prefix

    def _get_storage_location(self):
        return settings.get_root_dir()+self.storage_location

    def __make_filename(self, file_name):
        if self.unique_prefix:
            name = "%s/%s__%s" % (self._get_storage_location(), self.unique_prefix, file_name)
        else:
            name = "%s/%s" % (self._get_storage_location(), file_name)
        return name

    def __remove_filename_prefix(self, file_name):
        if self.unique_prefix:
            if file_name.startswith(self.unique_prefix):
                file_name = file_name[len(self.unique_prefix) + 2:]
        return file_name

    def loadFile(self, file_name):
        """
        Load the specified file from storage.

        @param file_name:    Name of the selected file.
        @type file_name:     string

        @return              Buffer containing the file contents.
        @rtype               string

        """
        try:
            f   = open(self.__make_filename(file_name), "r")
            buf = f.read()
            f.close()
        except Exception, e:
            raise RestxFileNotFoundException("File '%s' could not be found'" % (file_name))
        return buf

    def storeFile(self, file_name, data):
        """
        Store the specified file in storage.

        @param file_name:    Name of the file.
        @type file_name:     string

        @param data:         Buffer containing the file contents.
        @type data:          string

        """
        f = open(self.__make_filename(file_name), "w")
        f.write(data)
        f.close()

    def deleteFile(self, file_name):
        """
        Delete the specified file from storage.

        @param file_name:    Name of the selected file.
        @type file_name:     string

        """
        try:
            os.remove(self.__make_filename(file_name))
        except OSError, e:
            if e.errno == 2:
                raise RestxFileNotFoundException(file_name)
            elif e.errno == 13:
                raise RestxPermissionDeniedException(file_name)
            else:
                raise RestxException("Cannot delete file '%s (%s)'" % (file_name, str(e)))
        except Exception, e:
            raise RestxException("Cannot delete file '%s' (%s)" % (file_name, str(e)))

    def listFiles(self):
        """
        Return list of all files in the storage.

        @return:                 List of file names.
        @rtype:                  list

        """
        try:
            dir_list = os.listdir(self._get_storage_location())
            # Need to filter all those out, which are not part of our storage space
            if self.unique_prefix:
                our_files = [ name for name in dir_list if name.startswith(self.unique_prefix) ]
            else:
                our_files = dir_list
            no_prefix_dir_list = [ self.__remove_filename_prefix(name) for name in our_files ]
            return no_prefix_dir_list
        except Exception, e:
            raise RestxException("Problems getting file list from storage: " + str(e))

