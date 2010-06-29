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
Here we have all the defintions and implementations
for resource storage and access.

Storage is VERY simple at this point: We take the
unique name of the resource (also the last path element
of the resource's URI) as the filename under which we
store a JSON representation of the resource.

The stored representation of a resource looks like this:

    {
        "public": {
                    .... what a client can see, usually
                    the name, uri, description, sub_resources
                    and any available runtime-parameters.
                    This dictionary is returned when a
                    client requests information about a resource.
                  },
        "private": {
                    ... what was provided when the resource was
                    defined.
                   }
    }

"""

# Python imports
import os

# RESTx imports
import restx.settings as settings
from restx.platform_specifics import STORAGE_OBJECT

from org.mulesoft.restx.exception       import *
from restx.logger           import *
from restx.core.parameter   import TYPE_COMPATIBILITY
from restx.languages import *

from org.mulesoft.restx.util import Url


EXCLUDED_NAMES = [ "readme.txt" ]
EXCLUDE_PREFIXES = [ "_" ]

def getResourceUri(resource_name):
    """
    Construct a resource's URI based on its name.

    @return:  URI of the named resource.
    @rtype:   string
    
    """
    return settings.PREFIX_RESOURCE + "/" + resource_name


def retrieveResourceFromStorage(uri, only_public=False):
    """
    Return the details about a stored resource.
    
    The resource is identified via its URI.
    
    @param uri:         Identifies a resource via its URI.
    @type  uri:         string
    
    @param only_public: Flag indicating whether we only want to see the
                        public information about this resource.
    @type only_public:  boolean
    
    @return:            Dictionary or None if not found.
    @rtype:             dict
    
    """
    # Need to take the resource URI prefix off to get the resource_name.
    resource_name = uri[len(settings.PREFIX_RESOURCE)+1:]
    obj = None
    try:
        obj = STORAGE_OBJECT.loadResourceFromStorage(resource_name)
        if not obj:
            raise Exception("Unknown resource: " + resource_name)
        if type(obj) is not dict  or  'public' not in obj:
            obj = None
            raise Exception("Missing top-level element 'public' or malformed resource.")
        public_obj = obj['public']
        # Do some sanity checking on the resource. Needs to contain
        # a few key elements at least.
        for mandatory_key in [ 'uri', 'desc', 'name' ]:
            if mandatory_key not in public_obj:
                public_obj = None
                raise Exception("Mandatory key '%s' missing in stored resource '%s'" % \
                                (mandatory_key, resource_name))
        if only_public:
            obj = public_obj
            
    except Exception, e:
        log("Malformed storage for resource '%s': %s" % (resource_name, str(e)), facility=LOGF_RESOURCES)
    return obj


def deleteResourceFromStorage(uri):
    """
    Delete a resource definition from storage.

    @param uri:   Uri of the resource
    @type  uri:   string

    """
    resource_name = uri[len(settings.PREFIX_RESOURCE)+1:]
    STORAGE_OBJECT.deleteResourceFromStorage(resource_name)

def listResources():
    """
    Return list of all stored resources.
    
    Data is returned as dictionary keyed by resource name.
    For each resource the complete URI, the name and the description
    are returned.
    
    @return: Dictionary of available resources.
    @rtype:  dict
    
    """
    dir_list = STORAGE_OBJECT.listResourcesInStorage()
    out = {}
    for resource_name in dir_list:
        rname = resource_name.lower()
        if rname not in EXCLUDED_NAMES  and  rname[0] not in EXCLUDE_PREFIXES:
            resource_dict = retrieveResourceFromStorage(getResourceUri(resource_name), only_public=True)
            if resource_dict:
                out[resource_name] = dict(uri=Url(resource_dict['uri']), desc=resource_dict['desc'])
            else:
                out[resource_name] = "Not found"
    return out


def paramSanityCheck(param_dict, param_def_dict, name_for_errors):
    """
    Check whether a provided parameter-dict is compatible
    with a parameter-definition-dict.
    
    The following checks are performed:
    
     * Are there any keys in the params that are not in the definition?
     * Are all required parameters present?
     * Are the types are compatible?
    
    Does not return anything but raises RestxException with
    meaningful error message in case of problem.
    
    The 'name_for_errors' is used in the error message and provides
    some context to make the error message more useful.
    
    @param param_dict:      The parameter dictionary provided (for example by the client).
    @type  param_dict:      dict
    
    @param param_def_dict:  The parameter definition as provided by the component (the code).
                            The provided parameters are checked against this definition.
    @type  param_def_dict:  dict
    
    @param name_for_errors: A section name, which helps to provide meaningful error messages.
    @type  name_for_errors: string
    
    @raise RestxException:    If the sanity check fails.
    
    """
    #
    # Check whether there are unknown parameters in the 'param' section
    # and also whether the type is compatible.
    #
    if param_dict  and  type(param_dict) is not dict:
        raise RestxException("The '%s' section has to be a dictionary" % name_for_errors)
    if param_def_dict  and  param_dict:
        for pname in param_dict:
            # Any unknown parameters
            if pname not in param_def_dict:
                raise RestxException("Unknown parameter in '%s' section: %s" % (name_for_errors, pname))
            # Sanity check the types
            type_str    = param_def_dict[pname]['type']
            param_value = param_dict[pname]
            param_type  = type(param_value)
            storage_types, runtime_types, conversion_func = TYPE_COMPATIBILITY[type_str]
            if param_type in runtime_types:
                pass
            elif param_type not in storage_types:
                try:
                    if conversion_func:
                        conversion_func(param_value)
                    else:
                        raise Exception("Cannot convert provided parameter type (%s) to necessary type(s) '%s'" % \
                                        (param_type, runtime_types))
                except Exception, e:
                    raise RestxException("Incompatible type for parameter '%s' in section '%s': %s" % \
                                       (pname, name_for_errors, str(e)))
                    
    #
    # Check whether all required parameters are present
    #
    for pname, pdict in param_def_dict.items():
        if pdict['required']  and  (not param_dict  or  pname not in param_dict):
            raise RestxMandatoryParameterMissingException("Missing mandatory parameter '%s' in section '%s'" % (pname, name_for_errors))

def fillDefaults(param_def_dict, param_dict):
    """
    Copy defaults values into parameter dictionary if not present.
    
    The parameter dictionaries may be defined with defaults.
    So, if the param_dict does not contain anything for those
    parameters then we will create them in there with the
    default value that were specified in the parameter definition.
    
    @param param_def_dict:  The parameter definition- including default values -
                            provided by the component code.
    @type  param_def_dict:  dict
    
    @param param_dict:      The parameter definition provided by the client.
    @type  param_dict:      dict
    
    """
    for pname, pdict in param_def_dict.items():
        if not pdict['required']  and  pname not in param_dict:
            if pdict['default'] is not None:
                param_dict[pname] = pdict['default']

def convertTypes(param_def_dict, param_dict):
    """
    Convert parameters to those types indicated in the parameter definition.

    This is useful when we get parameters, such as the URL command line, where
    all is passed as string.

    @param param_def_dict:  The parameter definition- including default values -
                            provided by the component code.
    @type  param_def_dict:  dict
    
    @param param_dict:      The parameter definition provided by the client.
    @type  param_dict:      dict

    """
    for pname in param_dict:
        type_str   = param_def_dict[pname]['type']
        param_val  = param_dict[pname]
        param_type = type(param_val)
        storage_types, runtime_types, conversion_func = TYPE_COMPATIBILITY[type_str]
        if param_type in runtime_types:
            pass
        elif param_type not in storage_types:
            try:
                if conversion_func:
                    param_dict[pname] = conversion_func(param_val)
                else:
                    raise Exception("Cannot convert provided parameter type (%s) to necessary type(s) '%s'" % \
                                    (param_type, runtime_types))
            except Exception, e:
                raise RestxException("Incompatible type for parameter '%s': %s" % (pname, str(e)))


def makeResource(component_class, params):
    """
    Create a new resource representation from the
    specified component class and parameter dictionary
    and store it on disk.
        
    The parameters need to look something like this:
    
            {
                "reource creation_params" : {
                        "suggested_name" : "my_twitter",
                        "desc"           : "Our Twitter stream"
                },
                "params" : {
                        "user"     : "AccountName",
                        "password" : "some password"
                },
                "positional_params" : [ "user" ]      # Optional
            }

    The method performs sanity checking on the supplied
    parameters and also fills in default values where
    available.
    
    @param component_class:    A class (not instance) derived from BaseComponent.
    @type  component_class:    BaseComponent or derived.
    
    @param params:        The resource parameters provided by the client.
                          Needs to contain at least a 'params' dictionary
                          or a 'resource_creation_dictionary'. Can contain
                          both.
    @type  params:        dict
    
    @return:              Success message in form of dictionary that contains
                          "status", "name" and "uri" fields.
    @rtype:               dict
    
    @raise RestxException:  If the resource creation failed or there was a
                          problem with the provided parameters.

    """    
    # We get the meta data (parameter definition) from the component
    component            = component_class()
    component_params_def = component.getMetaData()
    component_params_def = languageStructToPython(component, component_params_def)

    #
    # First we check whether there are any unknown parameters specified
    # on the top level.
    #
    if type(params) is not dict:
        raise RestxException("Malformed resource parameter definition. Has to be JSON dictionary.")
        
    for k in params.keys():
        if k not in [ 'params', 'resource_creation_params' ]:
            raise RestxException("Malformed resource parameter definition. Unknown key: %s" % k)
    #
    # Check whether there are unknown parameters in the 'param' or 'resource_creation_params' section.
    #
    provided_params = params.get('params')
    if not provided_params:
        # If no parameters were provided at all, we create them as
        # an empty dictionary. We need something here to be able
        # to merge some defaults into it later on.
        provided_params = dict()
        params['params'] = provided_params
    provided_resource_creation_params = params.get('resource_creation_params')
    paramSanityCheck(provided_params, component_params_def['params'], 'params')
    paramSanityCheck(provided_resource_creation_params,
                     component_params_def['resource_creation_params'],
                     'resource_creation_params')

    # The parameters passed the sanity checks. We can now create the resource definition.
    suggested_name = provided_resource_creation_params['suggested_name']
    resource_uri   = settings.PREFIX_RESOURCE + "/" + suggested_name
    resource_name  = suggested_name # TODO: Should check if the resource exists already...
    params['code_uri'] = component.getCodeUri()  # Need a reference to the code that this applies to
    
    # Some parameters are optional. If they were not supplied,
    # we need to add their default values.
    fillDefaults(component_params_def['params'], provided_params)
    fillDefaults(component_params_def['resource_creation_params'], provided_resource_creation_params)

    # Storage for a resource contains a private and public part. The public part is what
    # any user of the resource can see: URI, name and description. In the private part we
    # store whatever was provided here during resource creation. It contains the information
    # we need to instantiate a running resource.
    resource_def = {
        "private" : params,
        "public"  : {
                        "uri"  : resource_uri,
                        "name" : resource_name,
                        "desc" : provided_resource_creation_params['desc']
                    }
    }
    
    # Storage to our 'database'.
    STORAGE_OBJECT.writeResourceToStorage(resource_name, resource_def)

    # Send a useful message back to the client.
    success_body = {
        "status" : "created",
        "name"   : resource_name,   # Is returned, because server could have chosen different name
        "uri"    : resource_uri
    }

    return success_body

    

