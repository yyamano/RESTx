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
Definition of the L{RestxComponent} class.

This represents a component that resides on a RESTx server.
The object is used for introspection (finding out about
the component meta data, the available services and any
parameters) as well as a starting point for resource
creation.

"""

from restxclient.restx_client_exception import RestxClientException
from restxclient.restx_parameter        import RestxParameter
from restxclient.restx_service          import RestxService
from restxclient.restx_resourcetemplate import RestxResourceTemplate

class RestxComponent(object):
    """
    Represents information about a component on a RESTx server.

    This representation can be used by clients to find out about
    component capabilities and also as a starting point to create
    new resources, by utilizing the L{get_resource_template}() function.

    """
    # The keys to the component's meta data dictionary.
    __NAME_KEY                      = "name"
    __DESC_KEY                      = "desc"
    __DOC_KEY                       = "doc"
    __URI_KEY                       = "uri"
    __PARAMS_KEY                    = "params"
    __RCP_KEY                       = "resource_creation_params"
    __RCP_DESC_KEY                  = "desc"
    __RCP_SUGGESTED_NAME_KEY        = "suggested_name"
    __SERVICES_KEY                  = "services"

    __server                        = None   # Reference to the server on which we reside (RestxServer)
    __name                          = None   # Name of this component
    __description                   = None   # Description of this component
    __doc_uri                       = None   # URI of docs for this component
    __doc                           = None   # Docs for this component
    __uri                           = None   # URI of this component
    __parameters                    = None   # Dictionary of parameter definitions
    __rcp_description_param         = None   # Definition of the fixed 'resource description' parameter
    __rcp_suggested_name_param      = None   # Definition of the fixed 'suggested name' parameter
    __services                      = None   # Dictionary of service definitions

    def __init__(self, server, cdesc):
        """
        Create a new component representation in memomory.

        @param server:      The RESTx server on which the component resides.
        @type server:       L{RestxServer}

        @param cdesc:       Dictionary describing the server component. This
                            is the dictionary returned by the server when a
                            component URI is accessed.
        @type cdesc:        dict

        """
        self.__server = server
        try:
            self.__name        = cdesc[self.__NAME_KEY]
            self.__description = cdesc[self.__DESC_KEY]
            self.__doc_uri     = cdesc[self.__DOC_KEY]
            self.__uri         = cdesc[self.__URI_KEY]
            pdict              = cdesc[self.__PARAMS_KEY]
            sdict              = cdesc[self.__SERVICES_KEY]

            # Parse the parameter dictionary and attempt to translate
            # this to a dictionary of proper RestxParameter objects.
            self.__parameters = dict()
            for pname, pdef in pdict.items():
                self.__parameters[pname] = RestxParameter(pname, pdef)

            # Set the resource creation time parameters, which
            # are always the same for every component. When we
            # create those parameter definitions we specify the
            # dictionary key as the name of the parameter, don't
            # be surprised...
            self.__rcp_description_param    = RestxParameter(self.__RCP_DESC_KEY,           cdesc[self.__RCP_KEY][self.__RCP_DESC_KEY])
            self.__rcp_suggested_name_param = RestxParameter(self.__RCP_SUGGESTED_NAME_KEY, cdesc[self.__RCP_KEY][self.__RCP_SUGGESTED_NAME_KEY])

            # Parse the service dictionary and attempt to translate
            # this to a dictionary of proper RestxService objects.
            self.__services = dict()
            for sname, sdef in sdict.items():
                self.__services[sname] = RestxService(sname, sdef)

        except KeyError:
            raise RestxClientException("Server error: Expected key '%s' missing in definition of component '%s'." % (str(e), self.__name))

    def _create_resource(self, rdict):
        """
        Create a new resource for this component on the server.

        Clients should NOT use this method directly. Instead, they
        should use obtain a resource template from the component and
        then call create_resource() on that template.

        @param rdict:   The completed dictionary to be posted to
                        this components URI.
        @type rdict:    dict

        """
        return self.__server._create_resource(self.__uri, rdict)

    def get_name(self):
        """
        Return the name of the component.

        @return:    Name of component.
        @rtype:     string

        """
        return self.__name

    def get_description(self):
        """
        Return the description of the component.

        @return:    Description of the component.
        @rtype:     string

        """
        return self.__description

    def get_docs(self):
        """
        Return the doc string of the component.

        @return:    Documentation of the component.
        @rtype:     string

        """
        if not self.__doc:
            status, self.__doc = self.__server._json_send(self.__doc_uri, status=200)
            
        return self.__doc

    def get_uri(self):
        """
        Return the URI of the component.

        @return:    URI of the component.
        @rtype:     string

        """
        return self.__uri

    def get_server(self):
        """
        Return the RestxServer structure of the server on which this component lives.

        @return:    The server of this component.
        @rtype:     L{RestxServer}

        """
        return self.__server

    def get_resource_description(self):
        """
        Return parameter definition for resource description parameter.

        @return:    The resource description parameter definition.
        @rtype:     L{RestxParameter}

        """
        return self.__rcp_description_param

    def get_resource_suggested_name(self):
        """
        Return parameter definition for resource suggested name parameter.

        @return:    The resource suggested name parameter definition.
        @rtype:     L{RestxParameter}

        """
        return self.__rcp_suggested_name_param

    def get_all_parameters(self):
        """
        Return all parameters defined for this component.

        @return:    Dictionary of all parameters.
        @rtype:     dict of L{RestxParameter}

        """
        return self.__parameters

    def get_parameter(self, name):
        """
        Return one parameters of this component.

        @param name:    Name of the parameter.
        @type name:     string

        @return:        Dictionary of all parameters.
        @rtype:         L{RestxParameter}

        """
        try:
            return self.__parameters[name]
        except KeyError:
            raise RestxClientException("Parameter '%s' not defined." % name)

    def get_all_services(self):
        """
        Return all services defined for this component.

        @return:    Dictionary of all services.
        @rtype:     dict of L{RestxService}

        """
        return self.__services

    def get_service(self, name):
        """
        Return one service of this component.

        @param name:    Name of the service.
        @type name:     string

        @return:        Dictionary of service definition.
        @rtype:         L{RestxService}

        """
        try:
            return self.__services[name]
        except KeyError:
            raise RestxClientException("Service '%s' not defined." % name)

    def get_resource_template(self):
        """
        Return a resource template for this component.

        @return:        Resource template.
        @rtype:         L{RestxResourceTemplate}

        """
        return RestxResourceTemplate(self)

    #
    # For convenience, we offer read access to several
    # elements via properties.
    #
    name        = property(get_name, None)
    docs        = property(get_docs, None)
    description = property(get_description, None)
    uri         = property(get_uri, None)
    server      = property(get_server, None)

