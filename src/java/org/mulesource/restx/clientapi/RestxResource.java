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
 * Represents information about a resource on a RESTx server.
 *
 * This representation can be used by clients to find out about
 * component capabilities and also as a starting point to create
 * new resources, by utilizing the get_resource_template() function.
 */
public class RestxResource
{
    protected final static String                   NAME_KEY     = "name";
    protected final static String                   DESC_KEY     = "desc";
    protected final static String                   URI_KEY      = "uri";
    protected final static String                   SERVICES_KEY = "services";

    protected final static String[]                 REQUIRED_KEYS  = { NAME_KEY, DESC_KEY, URI_KEY, SERVICES_KEY };

    protected RestxServer                             server;
    protected String                                name;
    protected String                                description;
    protected String                                uri;    
    protected HashMap<String, RestxAccessibleService> services;
    
    /**
     * Create a new client-side resource representation.
     * 
     * @param server  The RestxServer on which this resource resides.
     * @param rdesc   The dictionary describing the resource. This is the
     *                dictionary returned by the server when a resource
     *                URI is accessed.
     *                
     * @throws RestxClientException
     */
    public RestxResource(RestxServer server, HashMap<String, ?> rdesc) throws RestxClientException
    {
        this.server = server;
        try {
            // Sanity check on received information
            RestxServer.checkKeyset(rdesc, REQUIRED_KEYS);

            description       = (String)rdesc.get(DESC_KEY);
            uri               = (String)rdesc.get(URI_KEY);
            
            // Parse the service dictionary and attempt to translate
            // this to a dictionary of proper RestxAccessibleService objects.
            HashMap<String, HashMap<String, ?>> sdict =
                                            (HashMap<String, HashMap<String, ?>>)rdesc.get(SERVICES_KEY);
        
            services = new HashMap<String, RestxAccessibleService>();
            for (String sname: sdict.keySet()) {
                services.put(sname, new RestxAccessibleService(this, sname, sdict.get(sname)));
            }            
        }
        catch (RestxClientException e) {
            throw new RestxClientException("Malformed resource definition: " + e.getMessage());
        }
    }
    
    /**
     * Returns the name of the resource.
     * 
     * @return  Name of the resource.
     */
    public String getName()
    {
        return name;
    }

    /**
     * Returns the description of the resource.
     * 
     * @return  Description of the resource.
     */
    public String getDescription()
    {
        return description;
    }

    /**
     * Returns the URI of the resource.
     * 
     * @return  URI of the resource.
     */
    public String getUri()
    {
        return uri;
    }
    
    /**
     * Returns the server on which this resource resides.
     * 
     * @return  Reference to the RESTx server.
     */
    public RestxServer getServer()
    {
        return server;
    }
    
    /**
     * Returns a map of all the services offered by this resource.
     * 
     * @return  Map of services.
     */
    public HashMap<String, RestxAccessibleService> getAllServices()
    {
        return services;
    }
    
    /**
     * Return one service of this resource.
     * 
     * @param   name  Name of the service.
     * @return        A RESTx service object.
     * 
     * @throws        RestxClientException
     */
    public RestxAccessibleService getService(String name) throws RestxClientException
    {
        RestxAccessibleService service = services.get(name);
        if (service == null) {
            throw new RestxClientException("Service '" + name + "' is not defined.");
        }
        return service;
    }
    
    /**
     * Delete this resource from the server.
     * 
     * This local object becomes unusable after this operation.
     * 
     * @throws RestxClientException
     */
    public void delete() throws RestxClientException
    {
        server.send(uri, null, HttpMethod.DELETE, 200, null);
    }
}


