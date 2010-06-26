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
The parameter class.

"""
from datetime import date
from datetime import time as time_class

from restx.platform_specifics       import PLATFORM, PLATFORM_JYTHON
from org.mulesource.restx.exception import RestxException

#
# Types for resource parameters
#
PARAM_STRING   = "string"
PARAM_PASSWORD = "password"
PARAM_BOOL     = "boolean"
PARAM_DATE     = "date"
PARAM_TIME     = "time"
PARAM_NUMBER   = "number"
PARAM_URI      = "uri"

KNOWN_BASIC_TYPES = [ PARAM_STRING, PARAM_PASSWORD, PARAM_BOOL, PARAM_DATE,
                      PARAM_TIME, PARAM_NUMBER, PARAM_URI ]


#
# Each entry in the following table has the format:
#    ( storage_types, runtime_types, conversion_func )
#
# 'storage_types' defines a list of types that this value may
# have after being read in via JSON. For example, 'date'
# will not be recognized by JSON, it is stored and loaded
# as a string. So, 'str' is one of the valid types for date
# parameters.
#
# 'runtime_types' is a list of types that are acceptable after
# proper conversion, so that we can actually work with that
# type in our programming language. For example, we really
# want dates to be of class 'date', which is why for date
# parameters we specify that type.
#
# 'conversion_func' is a function that can be used to convert
# from a storatge-type to a runtime-type. Calling this function
# also provides a proper sanity check, since those functions
# will throw errors if they fail.
#
# Note: Date is defined as YYYY-MM-DD
# Note: Time is defined as HH:MM:SS
# 
def __numstr_to_num(x):
    if type(x) in [ int, float ]:
        return x
    elif type(x) in [ str, unicode ]:
        try:
            return int(x)
        except:
            return float(x)
    # Can't convert anything else
    return None

def __bool_convert(x):
    if type(x) is bool:
        return x
    else:
        if x.lower() in [ "y", "yes", "true", "t", "1" ]:
            return True
        else:
            return False

#
# Type conversion turns out to be quite odd. The more languages
# we enable, the more 'similar' types we have to recognize and
# deal with. For example, a component may expect a number as
# attribute. For a Java component that might be a BigDecimal,
# for a Python component, it might just be int or float.
# So, considering Python as the base, we start by defining all
# the python types for a particular RESTx type. Then we add the
# types of the other languages if and when appropriate.
TYPES_DICT = {
    "STRING_TYPES"   : [ unicode, str ],
    "PASSWORD_TYPES" : [ unicode, str ],
    "BOOL_TYPES"     : [ bool ],
    "DATE_TYPES"     : [ unicode, str ],
    "TIME_TYPES"     : [ unicode, str ],
    "NUMBER_TYPES"   : [ int, float ],
    "URI_TYPES"      : [ unicode, str ],
}

if PLATFORM == PLATFORM_JYTHON:
    # Now selectively add some of the Java types
    from java.math import BigDecimal
    TYPES_DICT["NUMBER_TYPES"].append(BigDecimal)


TYPE_COMPATIBILITY = {
    PARAM_STRING   : (TYPES_DICT["STRING_TYPES"], [ str ], None),
    PARAM_PASSWORD : (TYPES_DICT["PASSWORD_TYPES"], [ str ], None),
    PARAM_BOOL     : (TYPES_DICT["BOOL_TYPES"], [ bool ], __bool_convert),
    PARAM_DATE     : (TYPES_DICT["DATE_TYPES"], [ date ], lambda x : date(*[ int(elem) for elem in x.split("-")])),
    PARAM_TIME     : (TYPES_DICT["TIME_TYPES"], [ time_class ], lambda x : time_class(*[ int(elem) for elem in x.split(":")])),
    PARAM_NUMBER   : (TYPES_DICT["NUMBER_TYPES"], [ int, float ], __numstr_to_num),
    PARAM_URI      : (TYPES_DICT["URI_TYPES"], [ str ], None)
}

class ParameterDef(object):
    """
    This class encapsulates a parameter definition.
    
    Parameters are defined by each individual component.
    Therefore, in its __init__() method each component
    has to create its dictionary of ParameterDef classes
    and make it available via the getParams() method.
    
    By default, a parameter is 'required'. Note that
    this parameter definition does not contain the
    name of the parameter, since the name is merely
    the key in the parameter definition dictionary,
    which is maintained by each component.
    
    """
    def __init__(self, ptype, desc="", required=True, default=None):
        """
        Define a new parameter.
        
        A parameter is defined with the following attributes:
        
        @param ptype:            A type, such as PARAM_STRING, etc.
        @type prtype:            string
                
        @param desc:             A short, one-line description in human readable form.
        @type desc:              string
        
        @param required:         A flag indicating whether this parameter needs to be
                                 set by the resource creator, or whether a default
                                 value can be used.
        @type required:          boolean
        
        @param default:          A default value for this parameter of a suitable type.
                                 Only used if 'required == False'.
        @type default:           Whatever is needed as default value
        
        """
        self.ptype            = ptype
        self.desc             = desc
        self.required         = required
        if not self.required and default is None:
            raise RestxException("A default value is required for optional parameters")
        self.default          = default

    def getDefaultVal(self):
        """
        Return default value.

        Javaesque naming convention, because the method was first needed
        on the Java side of things.

        @return: The default value.
        @rtype:  object

        """
        return self.default
        
    def as_dict(self):
        """
        Unwraps this single parameter definition into a plain dictionary.
        
        Needed for browsing or accessing the component's meta info.
        
        @return:  Dictionary representation of the parameter.
        @rtype:   dict
        
        """
        return dict(type             = self.ptype,
                    desc             = self.desc,
                    required         = self.required,
                    default          = self.default)

    def html_type(self, name):
        """
        Return the HTML form field typoe for a value of this type.

        Needed when we display a resource creation form.

        @return:  A string containing "checkbox" or "text"
        @rtype:   string

        """
        if self.ptype == PARAM_BOOL:
            return '''<label for="%s_yes"><input type="radio" id="%s_yes" name="%s" value="yes" />yes</label><br>
                      <label for="%s_no"><input type="radio" id="%s_no" name="%s" value="no" />no</label>''' % (name, name, name, name, name, name)
        else:
            return '<input type="text" name="%s" />' % name

