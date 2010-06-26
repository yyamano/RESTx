/*      
 *  RESTx: Sane, simple and effective data publishing and integration. 
 *  
 *  Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com 
 *  
 *  This program is free software: you can redistribute it and/or modify 
 *  it under the terms of the GNU General Public License as published by 
 *  the Free Software Foundation, either version 3 of the License, or 
 *  (at your option) any later version. 
 * 
 *  This program is distributed in the hope that it will be useful, 
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of 
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 *  GNU General Public License for more details. 
 * 
 *  You should have received a copy of the GNU General Public License 
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>. 
 */ 


package org.mulesource.restx.clientapi;

import java.util.HashMap;

/**
 * Represents a template that can be used by a client to create a new resource.
 *
 * This representation can be used by clients to find out about
 * component capabilities and also as a starting point to create
 * new resources, by utilizing the getResourceTemplate() method.
 */
public class RestxResourceTemplate
{
    protected final static String     PARAMS_KEY             = "params";
    protected final static String     RCP_KEY                = "resource_creation_params";
    protected final static String     RCP_DESC_KEY           = "desc";
    protected final static String     RCP_SUGGESTED_NAME_KEY = "suggested_name";

    protected RestxComponent            component;
    protected HashMap<String, Object> paramValues;
    protected HashMap<String, Object> resourceCreationParamValues;

    /**
     * Create a new resource template in memory.
     *
     * @param component  The RestxComponent which created this template.
     */
    public RestxResourceTemplate(RestxComponent component)
    {
        this.component              = component;
        paramValues                 = new HashMap<String, Object>();
        resourceCreationParamValues = new HashMap<String, Object>();
    }
    
    /**
     * Returns all parameters defined for this template's component.
     * 
     * @return  Map of parameters.
     */
    public HashMap<String, RestxParameter> getAllParameters()
    {
        return component.getAllParameters();
    }
    
    /**
     * Return one parameter of this template's component.
     * 
     * @param  name  Name of the parameter.
     * @return       Representation of this parameter.
     */
    public RestxParameter getParameter(String name)
    {
        return component.getParameter(name);
    }
    
    /**
     * Return parameter definition for this template's resource description parameter.
     * 
     * @return  Representation of this parameter.
     */
    public RestxParameter getResourceDescription()
    {
        return component.getResourceDescription();
    }

    /**
     * Return parameter definition for this template's suggested name parameter.
     * 
     * @return  Representation of this parameter.
     */
    public RestxParameter getResourceSuggestedName()
    {
        return component.getSuggestedName();
    }
    
    /**
     * Set a parameter value for a given parameter.
     *
     * Performs proper sanity checking on the type and value.
     *
     * @param name   Name of the parameter.
     * @param value  Value object for that parameter.
     * 
     * @return       Reference to ourselves so that set() calls can be chained.
     * 
     * @throws       RestxClientException
     */
    public RestxResourceTemplate set(String name, Object value) throws RestxClientException
    {
        RestxParameter pdef = getParameter(name);
        pdef.sanityCheck(value);
        paramValues.put(name, value);
        return this;
    }
    
    /**
     * Sets the 'description' resource creation time parameter.
     * 
     * @param  desc  The description for the new resource.
     * @return       Reference to ourselves so that set...() calls can be chained.
     */
    public RestxResourceTemplate setDescription(String desc)
    {
        resourceCreationParamValues.put(RCP_DESC_KEY, desc);
        return this;
    }
    
    /**
     * Sets the 'suggested name' resource creation time parameter.
     * 
     * @param  name  The suggested name for the new resource.
     * @return       Reference to ourselves so that set...() calls can be chained.
     */
    public RestxResourceTemplate setSuggestedName(String name)
    {
        resourceCreationParamValues.put(RCP_SUGGESTED_NAME_KEY, name);
        return this;
    }
    
    public RestxResource createResource() throws RestxClientException
    {
        // Check whether all required parameters have been set
        HashMap<String, RestxParameter> parameters = getAllParameters();
        if (parameters != null  &&  !parameters.isEmpty()) {
            for (String pname: parameters.keySet()) {
                if (parameters.get(pname).isRequired()  &&  !paramValues.containsKey(pname)) {
                    throw new RestxClientException("Required parameter '" + pname + "' is missing.");
                }
            }
        }
        
        // Assemble the resource creation dictionary, which is sent
        // to the component URI in order to create a resource on the
        // server.
        HashMap<String, Object> d = new HashMap<String, Object>();
        d.put(PARAMS_KEY, paramValues);
        d.put(RCP_KEY,    resourceCreationParamValues);
        HashMap<String, Object> res = component.createResource(d);
        
        // The server returned a dictionary with some information about
        // the outcome of the operation.
        String status = (String) res.get("status");
        if (status == null  ||  !status.equals("created")) {
            throw new RestxClientException("Resource could not be created.");
        }
        
        // Quickest way for us to get the resource is to just
        // get it directly from the server, using the name we
        // were given.
        String name = (String)res.get("name");
        return component.getServer().getResource(name);
    }

}


