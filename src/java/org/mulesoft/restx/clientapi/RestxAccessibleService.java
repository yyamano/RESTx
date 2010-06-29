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


package org.mulesoft.restx.clientapi;

import java.util.HashMap;

/**
 * Represents information about a service of a RESTx component or resource,
 * ready to be accessed.
 *
 * This representation can be used by clients to find out about
 * service capabilities and also to access the service methods of
 * the resource.
 */
public class RestxAccessibleService extends RestxService
{
    protected HashMap<String, Object> paramsVals;
    protected RestxResource             resource;
    protected String                  inputBuf;

    /**
     * This takes a service definition hash map as they would be received
     * straight from the server. No prior sanity checking needs to be performed
     * on it, since this constructor properly parses and interprets this map.
     * 
     * @param resource  The resource to which this accessible service belongs.
     * @param name      Name of the new service.
     * @param sdef      HashMap describing the service definition

     * @throws RestxClientException 
     */
    public RestxAccessibleService(RestxResource resource, String name, HashMap<String, ?> sdef) throws RestxClientException
    {
        super(name, sdef);
        this.paramsVals = new HashMap<String, Object>();
        this.resource   = resource;
        this.inputBuf   = null;
    }
    
    /**
     * Store a parameter value for the subsequent service invocation.
     * 
     * The string representation of the 'value' object is
     * stored. This parameter value will be passed on the
     * URL command line.
        
     * @param  name   Name of parameter.
     * @param  value  Value object of parameter.
     * @return        Reference to ourselves, so that set() calls can
     *                be chained.
     * 
     * @throws        RestxClientException
     */
    public RestxAccessibleService set(String name, Object value) throws RestxClientException
    {
        RestxParameter pdef = getParameter(name);
        pdef.sanityCheck(value);
        paramsVals.put(name, value.toString());
        
        return this;
    }

    /**
     * Specify an input buffer that's to be sent in the
     * request to the service method.
     * 
     * @param buffer  Content for the message body
     * @return        Reference to ourselves, so that set() calls can
     *                be chained.
     */
    public RestxAccessibleService setInput(String buffer)
    {
        inputBuf = buffer;
        return this;
    }
    
    /**
     * Sends the service request to the server.
     * 
     * @param  method  The HTTP request method. If an input was set then this
     *                 defaults to POST, otherwise GET.
     *                 
     * @return         A {@link HttpResult} object with information about the
     *                 server response.
     *                 
     * @throws         RestxClientException 
     */
    public HttpResult access() throws RestxClientException
    {
        return access(null);
    }
    
    /**
     * Sends the service request to the server.
     * 
     * @param  method  The HTTP request method. If this is null and an input
     *                 was set then this defaults to POST. If the caller requests
     *                 anything but PUT or POST with a set input then an exception
     *                 is thrown.
     *                 If no input was specified and this is set to null then the
     *                 method defaults to GET.
     *                 
     * @return         A {@link HttpResult} object with information about the
     *                 server response.
     *                 
     * @throws         RestxClientException 
     */
    public HttpResult access(HttpMethod method) throws RestxClientException
    {
        // Check whether all required parameters have been set
        if (parameters != null  &&  !parameters.isEmpty()) {
            for (String pname: parameters.keySet()) {
                if (parameters.get(pname).isRequired()  &&  !paramsVals.containsKey(pname)) {
                    throw new RestxClientException("Required parameter '" + pname + "' is missing.");
                }
            }
        }
        
        // Start creating the request URI
        StringBuilder reqUri = new StringBuilder(resource.getUri()).append("/").append(getName());
        
        // Assemble the query portion of the URL from the parameters
        boolean firstParam = true;
        for (String pname: paramsVals.keySet()) {
            if (!firstParam) {
                reqUri.append("&");
            }
            else {
                reqUri.append("?");
                firstParam = false;
            }
            reqUri.append(pname);
            reqUri.append("=");
            reqUri.append(paramsVals.get(pname));
        }
        String uri = reqUri.toString();
        
        if (method == null) {
            // Caller didn't specify a method, so we set a default one
            if (inputBuf != null) {
                method = HttpMethod.POST;
            }
            else {
                method = HttpMethod.GET;
            }
        }
        else {
            // A method was specified by the caller. Do some sanity checking.
            // Specifically: If an input was specified then the method must be
            // either POST or PUT.
            if (inputBuf != null) {
                if (method == HttpMethod.POST  ||  method == HttpMethod.PUT) {
                    throw new RestxClientException("Request method must be POST or PUT, " +
                                                 "because a message body (input) was set.");
                }
            }
            else {
                switch(method) {
                    case GET:
                    case POST:
                    case PUT:
                    case DELETE:
                        break;
                    default:
                        if (method == HttpMethod.POST  ||  method == HttpMethod.PUT) {
                            throw new RestxClientException("Cannot specify POST or PUT method " +
                                                         "without setting message body (input).");
                        }
                        else {
                            throw new RestxClientException("Unknown request method.");
                        }
                }
            }
        }
        return resource.getServer().jsonSend(uri, inputBuf, method, null, null);
    }
}

