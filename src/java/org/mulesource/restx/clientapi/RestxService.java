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

import java.util.ArrayList;
import java.util.HashMap;

/**
 * Represents information about a service of a RESTx component or resource.
 *
 * This representation can be used by clients to find out about
 * service capabilities.
 */
public class RestxService
{
    protected final static String           DESC_KEY              = "desc";
    protected final static String           URI_KEY               = "uri";
    protected final static String           PARAMS_KEY            = "params";
    protected final static String           POSITIONAL_PARAMS_KEY = "positional_params";

    protected final static String[]         REQUIRED_KEYS  = { DESC_KEY, URI_KEY };

    protected String                        name;
    protected String                        description;
    protected String                        uri;
    protected HashMap<String, RestxParameter> parameters;
    protected ArrayList<String>             positional_params;

    /**
     * Create a new RestxService definition.
     * 
     * This takes a service definition hash map as they would be received
     * straight from the server. No prior sanity checking needs to be performed
     * on it, since this constructor properly parses and interprets this map.
     * 
     * @param name  Name of the new service.
     * @param sdef  HashMap describing the service definition
     * 
     * @throws      RestxClientException 
     */
    public RestxService(String name, HashMap<String, ?> sdef) throws RestxClientException
    {
        this.name = name;
        try {
            // Sanity check on received information
            RestxServer.checkKeyset(sdef, REQUIRED_KEYS);

            description       = (String)sdef.get(DESC_KEY);
            uri               = (String)sdef.get(URI_KEY);
            positional_params = (ArrayList<String>)sdef.get(POSITIONAL_PARAMS_KEY);
            
            // Parse the parameter dictionary and attempt to translate
            // this to a dictionary of proper RestxParameter objects.
            HashMap<String, HashMap<String, ?>> pdict = (HashMap<String, HashMap<String, ?>>) sdef.get(PARAMS_KEY);
            if (pdict != null) {
                parameters = new HashMap<String, RestxParameter>();
                for (String pname: pdict.keySet()) {
                    parameters.put(pname, new RestxParameter(pname, pdict.get(pname)));
                }
            }
            else {
                parameters = null;
            }
        }
        catch (RestxClientException e) {
            throw new RestxClientException("Malformed service definition: " + e.getMessage());
        }
    }

    /**
     * Returns the name of the service.
     * 
     * @return  Name of service.
     */
    public String getName()
    {
        return name;
    }
    
    /**
     * Returns the description of the service.
     * 
     * @return  Description of the service.
     */
    public String getDescription()
    {
        return description;
    }

    /**
     * Returns the URI of the service.
     * 
     * @return  URI of the service.
     */
    public String getUri()
    {
        return uri;
    }
 
    /**
     * Return a map of all the parameter definitions for this service.
     * 
     * @return  Map of {@link RestxParameter} objects.
     */
    public HashMap<String, RestxParameter> getAllParameters()
    {
        return parameters;
    }
    
    /**
     * Return a single parameter definition.
     * 
     * @return  A single {@link RestxParameter} object.
     */
    public RestxParameter getParameter(String name)
    {
        return parameters.get(name);
    }

    /**
     * Return an array with all the positional parameter names.
     * 
     * The order of entries in that array reflects the order in
     * which the positional parameters need to be arranged.
     * 
     * @return  Names of all positional parameters.
     */
    public String[] getPositionalParamNames()
    {
        if (positional_params == null) {
            return null;
        }
        
        // Jump through hoops to get the hash-map keys as a String[],
        // because we can't just do a simple cast on the array.
        Object[] pp       = positional_params.toArray();
        String[] strArray = new String[pp.length];        
        System.arraycopy(pp, 0, strArray, 0, pp.length);
        return strArray;
    }
}


