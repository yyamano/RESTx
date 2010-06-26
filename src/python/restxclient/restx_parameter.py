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
Definition of the L{RestxParameter} class.

This object describes the properties of a paremeter.
Parameters are used in different contexts.

    - A resource creation time parameter of a component.
    - A parameter for a component service
    - A parameter for a resource service (sub-resource)

"""

from restxclient.restx_client_exception import RestxClientException

def _numstr_to_num(x):
    """
    Translate a string to a numeric value.

    This sort of translation function is necessary to be more
    flexible in handling the type of input for parameter values.

    @param x:    String representing a number or a number
                 type.
    @type x:     string or number type

    @return:     Numeric value
    @rtype:      Integer or Float

    """
    if type(x) in [ int, float ]:
        return x
    try:
        return int(x)
    except:
        return float(x)

def _bool_convert(x):
    """
    Translate a string to a boolean value.

    This sort of translation function is necessary to be more
    flexible in handling the type of input for parameter values.

    Strings like 'y', 'yes', 'true', 't', '1' are interpreted
    as True, all other strings are considered to mean False.

    It works for upper and lower-case strings.

    @param x:     String representation of a boolean value
                  or a boolean.
    @type x:      string or boolean

    @return:      Boolean value.
    @rtype:       boolean

    """
    if type(x) is bool:
        return x
    if x.lower() in [ "y", "yes", "true", "t", "1" ]:
        return True
    else:
        return False


class RestxParameter(object):
    """
    Represents a parameter for a RESTx resource or service.

    This is a representation of the parameter's definition, not of the
    parameter's value.

    """
    # The keys to the parameter's meta data dictionary.
    __DESC_KEY     = "desc"
    __REQUIRED_KEY = "required"
    __TYPE_KEY     = "type"
    __DEFAULT_KEY  = "default"

    __name         = None
    __desc         = None
    __required     = None
    __default_val  = None
    __type_str     = None

    # All the known types identifiers for parameters
    __PARAM_STRING   = "string"
    __PARAM_PASSWORD = "password"
    __PARAM_BOOL     = "boolean"
    __PARAM_DATE     = "date"
    __PARAM_TIME     = "time"
    __PARAM_NUMBER   = "number"
    __PARAM_URI      = "uri"

    # This table can convert strings for specific types to a proper object
    # of the indicated type. The type identifier can be used to look up
    # a tuple, which contains suitable types as well as a suitable
    # conversion function. 'None' for the function indicates that no conversion
    # is necessary, since the underlying type is a string.
    __TYPE_CONVERT = {
        __PARAM_STRING   : ([str, unicode], None), 
        __PARAM_PASSWORD : ([str, unicode], None),
        __PARAM_BOOL     : ([str, unicode, bool], _bool_convert),
        __PARAM_DATE     : ([None], lambda x : date(*[ int(elem) for elem in x.split("-")])),
        __PARAM_TIME     : ([None], lambda x : time_class(*[ int(elem) for elem in x.split(":")])),
        __PARAM_NUMBER   : ([str, unicode, int, float], _numstr_to_num),
        __PARAM_URI      : ([str, unicode], None),
    }

    def __str__(self):
        """
        Return a string representation of this paramater.

        """
        return \
"""RestxParameter '%s':
    Description:   %s
    Type:          %s
    Required:      %s
    Default val:   %s""" % (self.__name, self.__desc, self.__type_str, self.__required, self.__default_val)

    def __init__(self, name, pdef):
        """
        Create a new parameter definition representation in memory.

        @param name:    Name of the parameter.
        @type name:     string

        @param pdef:    Dictionary with parameter definition. This is the
                        dictionary returned by the server when describing
                        a parameter.
        @type pdef:     dict

        """
        try:
            self.__name         = name
            self.__desc         = pdef[self.__DESC_KEY]
            self.__required     = _bool_convert(pdef.get(self.__REQUIRED_KEY, "n"))
            self.__type_str     = pdef[self.__TYPE_KEY].lower()

            if self.__type_str not in self.__TYPE_CONVERT:
                raise RestxClientException(("Server error: Type '%s' specified for parameter '%s', which is " +
                                          "not supported by this client library.") % (self.__type_str, self.__name))

            if self.__DEFAULT_KEY in pdef:
                # If a default value was specified, store it converted to
                # to the proper type.
                suitable_types, conversion_function = self.__TYPE_CONVERT[self.__type_str]
                value_str                           = pdef[self.__DEFAULT_KEY]
                if conversion_function:
                    self.__default_val = conversion_function(value_str)
                else:
                    self.__default_val = value_str
            else:
                if not self.__required:
                    raise RestxClientException("Server error: No default value specified for optional parameter '%s'." % self.__name)

        except KeyError, e:
            raise RestxClientException("Server error: Expected key '%s' missing in definition of parameter '%s'." % (str(e), self.__name))

    def sanity_check(self, value):
        """
        Check whether this is a valid value for this parameter.

        Raises an exception if there's a problem.

        @param value:      Some value object.
        @type value:       object

        """
        suitable_types, conversion_function = self.__TYPE_CONVERT[self.__type_str]
        if type(value) not in suitable_types:
            raise RestxClientException("Type '%s' is not suitable for parameter '%s'. Has to be one of '%s'." % (type(value), self.__name, suitable_types))

    def get_name(self):
        """
        Return the name of the parameter.

        @return:        Name of parameter.
        @rtype:         string

        """
        return self.__name

    def get_description(self):
        """
        Return the description of the parameter.

        @return:        Description of parameter.
        @rtype:         string

        """
        return self.__desc

    def get_parameter_type_str(self):
        """
        Return the string representation of the type of this parameter.

        @return:        String representation of parameter type.
        @rtype:         string

        """
        return self.__type_str

    def get_default_value(self):
        """
        Return the default value, if one was set.

        @return:        The default value, or None.
        @rtype:         Whichever type the default value has.

        """
        return self.__default_val

    def is_required(self):
        """
        Indicate whether this is a required parameter.

        @return:        Flag, which is True if required, False otherwise.
        @rtype:         boolean

        """
        return self.__required

    #
    # Some properties for conevenience
    #
    name        = property(get_name, None)
    description = property(get_description, None)
    required    = property(is_required, None)
    type_str    = property(get_parameter_type_str, None)

