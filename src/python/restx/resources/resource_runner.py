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


import restxjson as json

import restx.settings as settings

import restx.core.codebrowser  # Wanted to be much more selective here, but a circular
                             # import issue was most easily resolved like this.
                             # We only need getComponentInstance() from this module.

from org.mulesoft.restx.exception import *
from org.mulesoft.restx.component.api import HTTP, Result
from restx.resources  import paramSanityCheck, fillDefaults, convertTypes, \
                           retrieveResourceFromStorage, getResourceUri

from restx.languages import *

from restx.components.base_capabilities import BaseCapabilities


def _accessComponentService(component, services, complete_resource_def, resource_name, service_name,
                            positional_params, runtime_param_dict, input, request=None, method=None, direct_call=False):
    """
    Passes control to a service method exposed by a component.
    
    @param component:             An instance of the component.
    @type component:              BaseComponent (object of child class)
    
    @param services:              Dictionary of services definitions for this component. Can be had
                                  by calling _getServices() on the component. But we would need the
                                  resource's base URI to get those URIs exported properly. Since
                                  we already did this call in process() from where we called this
                                  method, we just pass the services dictionary in, rather than
                                  calling _getServices() again.
    @param services:              dict
    
    @param complete_resource_def: The entire resource definition as it was retrieved from storage.
    @type complete_resource_def:  dict
    
    @param resource_name:         Name of the resource. This may contain '/' if positional parameters
                                  are defined in the URL.
    @type resource_name:          string
    
    @param service_name:          The name of the requested service
    @type service_name:           string
    
    @param positional_params:     List of positional parameters.
    @type positional_params:      list

    @param runtime_param_dict:    Dictionary of URL command line arguments.
    @type runtime_param_dict:     dict
    
    @param input:                 Any potential input (came in the request body)
    @type input:                  string

    @param request:               HTTP request structure.
    @type request:                RestxHttpRequest
    
    @param method:                Http method of the request.
    @type method:                 HttpMethod
    
    @param direct_call:           Set this if the function is called directly from another component
                                  or piece of code that's not part of RESTx. In that case, it wraps
                                  the actual exception in a 'normal' exception and passes it up.
                                  That allows the framework code to react differently to exceptions
                                  in here than direct-call code.
    @type direct_call:            boolean
    
    @return                       HTTP result structure
    @rtype                        Result
    
    """
    try:
        service_def = services.get(service_name)
        if not service_def:
            raise RestxException("Service '%s' is not available in this resource." % service_name)

        #
        # Some runtime parameters may have been provided as arguments on
        # the URL command line. They need to be processed and added to
        # the parameters if necessary.
        #
        # Parameters may either appear as named arguments after the URL,
        # like this:  http://resource/somename?name1=val1&name2=val2
        #
        # If positional parameters are defined for the service then they
        # may be extracted from the URL. For example, if the positional
        # parameters are defined as [ "name1", "name2" ] then the URL can
        # be this: http://resource/somename/val1/val2/
        # With that URL and using the order that's defined in the
        # positional parameter definition, the values are assigned
        # like this: name1=val1, name2=val2
        #
        # Parameters specified in the first form (named arguments after '?')
        # override the same parameters specified in the URL itself.
        #
        # Why did we not check for those parameters earlier when the
        # runtime_param_dict parameter was created before this function
        # was called? Because we may have been called out of the accessResource()
        # method, which could possibly use a complete 
        #
        if positional_params:
            try:
                pos_param_def = complete_resource_def['public']['services'][service_name]['positional_params']
            except Exception, e:
                pos_param_def = None
            if pos_param_def:
                # Iterating over all the positional parameters that are provided in the URI
                # There might be some empty ones (when the URL has two // in a row or ends
                # in a /). In that case, we skip that parameter.
                pos_def_index = 0
                for value in positional_params:
                    if value:
                        pname = pos_param_def[pos_def_index]
                        pos_def_index += 1
                        # Put the new value in the runtime_parameter_dict, but only if it
                        # doesn't exist there already (parameters specified after a '?'
                        # are in there and they take precedence).
                        if pname not in runtime_param_dict:
                            runtime_param_dict[pname] = value
                    if pos_def_index == len(pos_param_def):
                        # No more positional parameters defined? We will ignore whatever
                        # else is in the URL
                        break
            
        runtime_param_def  = service_def.get('params')
        if runtime_param_def:
            # If the 'allow_params_in_body' flag is set for a service then we
            # allow runtime parameters to be passed in the request body PUT or POST.
            # So, if the URL command line parameters are not specified then we
            # should take the runtime parameters out of the body.
            # Sanity checking and filling in of defaults for the runtime parameters
            if service_def.get('allow_params_in_body')  and  input:
                # Take the base definition of the parameters from the request body
                try:
                    base_params = json.loads(input.strip())
                    input       = None  # The input is now 'used up'
                except ValueError, e:
                    # Probably couldn't parse JSON properly.
                    base_param = {}
                # Load the values from the body into the runtime_param_dict, but
                # only those which are not defined there yet. This allows the
                # command line args to overwrite what's specified in the body.
                for name, value in base_params.items():
                    if name not in runtime_param_dict:
                        runtime_param_dict[name] = value

            paramSanityCheck(runtime_param_dict, runtime_param_def, "runtime parameter")
            fillDefaults(runtime_param_def, runtime_param_dict)
            convertTypes(runtime_param_def, runtime_param_dict)
    
        services = complete_resource_def['public']['services']
        if service_name in services  and  hasattr(component, service_name):
            service_method = getattr(component, service_name)
            
            # Get the parameters from the resource definition time
            params = complete_resource_def['private']['params']

            if runtime_param_dict:
                # Merge the runtime parameters with the static parameters
                # from the resource definition.
                params.update(runtime_param_dict)

            component.setBaseCapabilities(BaseCapabilities(component))
            
            # A request header may tell us about the request body type. If it's
            # JSON then we first convert this to a plain object
            if request:
                req_headers = request.getRequestHeaders()
                if req_headers:
                    ct = req_headers.get("Content-type")
                    if ct  and  "application/json" in ct:
                        if input:
                            input = json.loads(input)

            result = serviceMethodProxy(component, service_method, service_name, request,
                                        input, params, method)
            return result
        else:
            raise RestxException("Service '%s' is not exposed by this resource." % service_name)
    except RestxException, e:
        if direct_call:
            raise Exception(e.msg)
        else:
            raise e


def _getResourceDetails(resource_name):
    """
    Extract and compute a number of importants facts about a resource.
    
    The information is returned as a dictionary.
    
    @param resource_name:    The name of the resource.
    @type resource_name:     string
    
    @return:                 Dictionary with information about the resource.
    @rtype:                  dict
    
    """
    complete_resource_def  = retrieveResourceFromStorage(getResourceUri(resource_name))
    if not complete_resource_def:
        raise RestxResourceNotFoundException("Unknown resource")
    resource_home_uri      = getResourceUri(resource_name)
    public_resource_def    = complete_resource_def['public']
    
    # Instantiate the component to get the exposed sub-services. Their info
    # is added to the public information about the resource.
    code_uri  = complete_resource_def['private']['code_uri']
    component = restx.core.codebrowser.getComponentInstance(code_uri, resource_name)
    services  = component._getServices(resource_home_uri)
    services  = languageStructToPython(component, services)
    public_resource_def['services'] = services
    
    return dict(complete_resource_def = complete_resource_def,
                resource_home_uri     = resource_home_uri,
                public_resource_def   = public_resource_def,
                code_uri              = code_uri,
                component             = component)

     
def accessResource(resource_uri, input=None, params=None, method=HTTP.GET):
    """
    Access a resource identified by its URI.
    
    @param resource_name:    The uri of the resource. We allow absolute URIs (well, later at least),
                             and relative URIs (starting with "/resource/").
                             Contains resource name, service name and any positional parameters.
    @type resource_name:     string
    
    @param service_name:     Name of the desired service
    @type service_name:      string
    
    @param input:            Any input information that may have been sent with the request body.
    @type input:             string
    
    @param params:           Any run-time parameters for this service as key/value pairs.
    @type params:            dict
    
    @param method:           The HTTP method to be used.
    @type method:            HttpMethod
    
    """
    if not resource_uri.startswith(settings.PREFIX_RESOURCE + "/"):
        raise Exception("Malformed resource name. Needs to be absolute or start with '%s'" % settings.PREFIX_RESOURCE)
    resource_uri = resource_uri[len(settings.PREFIX_RESOURCE)+1:]   # Strip the prefix off

    # Get the public representation of the resource
    path_components   = resource_uri.split("/")
    resource_name     = path_components[0]
    try:
        service_name  = path_components[1]
    except:
        raise RestxBadRequestException("Service method missing")

    positional_params = path_components[2:]   # Doesn't throw exception if not present, just yields []

    rinfo = _getResourceDetails(resource_name)

    if params is None:
        params = dict()
    
    result = _accessComponentService(rinfo['component'], rinfo['public_resource_def']['services'],
                                     rinfo['complete_resource_def'], resource_name,
                                     service_name, positional_params, params, input, None, method, True)
    return result.getStatus(), result.getEntity()
 
 
