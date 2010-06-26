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
Definition of the L{RestxResource} class.

"""

from restxclient.restx_client_exception import RestxClientException
from restxclient.restx_parameter        import RestxParameter
from restxclient.restx_service          import RestxAccessibleService

class RestxResource(object):
    """
    Represents information about a resource on a RESTx server.

    This representation can be used by clients to find out about
    component capabilities and also as a starting point to create
    new resources, by utilizing the get_resource_template() function.

    """
    # The keys to the component's meta data dictionary.
    __NAME_KEY                      = "name"
    __DESC_KEY                      = "desc"
    __URI_KEY                       = "uri"
    __SERVICES_KEY                  = "services"

    __server                        = None   # Reference to the server on which we reside (RestxServer)
    __name                          = None   # Name of this resource
    __description                   = None   # Description of this resource
    __uri                           = None   # URI of this resource
    __services                      = None   # Dictionary of service definitions

    def __init__(self, server, rdesc):
        """
        Create a new resource representation in memomory.

        @param server:      The RESTx server on which the resource resides.
        @type server:       L{RestxServer}

        @param rdesc:       Dictionary describing the server resource. This
                            is the dictionary returned by the server when a
                            reource URI is accessed.
        @type rdesc:        dict

        """
        self.__server = server
        try:
            self.__name        = rdesc[self.__NAME_KEY]
            self.__description = rdesc[self.__DESC_KEY]
            self.__uri         = rdesc[self.__URI_KEY]
            sdict              = rdesc[self.__SERVICES_KEY]

            # Parse the service dictionary and attempt to translate
            # this to a dictionary of proper RestxAccessibleService objects.
            self.__services = dict()
            for sname, sdef in sdict.items():
                self.__services[sname] = RestxAccessibleService(self, sname, sdef)

        except KeyError, e:
            raise RestxClientException("Server error: Expected key '%s' missing in definition of resource '%s'." % (str(e), self.__name))

    def __str__(self):
        """
        Return a string representation of this resource.

        """
        buf = \
"""RestxResource: %s
    Description:  %s
    URI:          %s
    Services:""" % (self.__name, self.__description, self.__uri)
        if self.__services:
            for sname, sdef in self.__services.items():
                buf += "\n----------------\n" + str(sdef)
        return buf

    def get_name(self):
        """
        Return the name of the resource.

        @return:    Name of resource.
        @rtype:     string

        """
        return self.__name

    def get_description(self):
        """
        Return the description of the resource.

        @return:    Description of the resource.
        @rtype:     string

        """
        return self.__description

    def get_uri(self):
        """
        Return the URI of the resource.

        @return:    URI of the resource.
        @rtype:     string

        """
        return self.__uri

    def get_server(self):
        """
        Return the L{RestxServer} object of the server on which this resource lives.

        @return:    The server of this resource.
        @rtype:     L{RestxServer}

        """
        return self.__server

    def get_all_services(self):
        """
        Return all services defined for this resource.

        @return:    Dictionary of all services.
        @rtype:     dict of L{RestxAccessibleService}

        """
        return self.__services

    def get_service(self, name):
        """
        Return one service of this resource.

        @param name:    Name of the service.
        @type name:     string

        @return:        Dictionary of service definition.
        @rtype:         L{RestxAccessibleService}

        """
        try:
            return self.__services[name]
        except KeyError:
            raise RestxClientException("Service '%s' not defined." % name)

    def delete(self):
        """
        Delete the resource on the server.

        """
        self.__server._send(self.__uri, method="DELETE", status=200)

    #
    # For convenience, we offer read access to several
    # elements via properties.
    #
    name        = property(get_name, None)
    description = property(get_description, None)
    uri         = property(get_uri, None)
    server      = property(get_server, None)

