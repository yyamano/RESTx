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

/**
 * A type for the known HTTP methods.
 */
public enum HttpMethod
{
    GET,
    PUT,
    POST,
    DELETE,
    OPTIONS,
    HEAD,
    UNKNOWN;
        
    /**
     * Convert an HttpMethod to a string representation of the method.
     * 
     * @param   method    The HttpMethod instance for which we want the
     *                    string representation.
     * @return            A string representation of the HttpMethod.
     */
    public static String toString(HttpMethod method)
    {
        if (method == GET) {
            return "GET";
        }
        else if (method == PUT) {
            return "PUT";
        }
        else if (method == POST) {
            return "POST";
        }
        else if (method == DELETE) {
            return "DELETE";
        }
        else if (method == OPTIONS) {
            return "OPTIONS";
        }
        else if (method == HEAD) {
            return "HEAD";
        }
        else {
            return "UNKNOWN";
        }
    }
    
    /**
     * Create a new HttpMethod object from a string representation.
     * 
     * @param   method   String representation of the method. Must be
     *                   uppercase.
     * @return           A new HttpMethod object for this method.
     */
    public static HttpMethod fromString(String method)
    {
        if (method.equals("GET")) {
            return GET;
        }
        else if (method.equals("POST")) {
            return POST;
        }
        else if (method.equals("PUT")) {
            return PUT;
        }
        else if (method.equals("DELETE")) {
            return DELETE;
        }
        else if (method.equals("OPTIONS")) {
            return OPTIONS;
        }
        else if (method.equals("HEAD")) {
            return HEAD;
        }
        else {
            return UNKNOWN;
        }
    }
}


