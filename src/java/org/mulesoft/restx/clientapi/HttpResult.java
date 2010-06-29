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
 * The result of an HTTP request.
 */
public class HttpResult
{
    /**
     * The HTTP status that was returned for this request.
     */
    public int    status;
    
    /**
     * The data that was returned.
     * 
     * In some cases the data might have been de-serialized
     * already, which is why this is a generic Object type.
     * The caller needs to cast this data to the type it wants
     * to deal with.
     */
    public Object data;
    
    /**
     * Create a new HTTP result object.
     * 
     * @param status    The status returned by the server.
     * @param data      The data returned by the server.
     */
    public HttpResult(int status, Object data)
    {
        this.status = status;
        this.data   = data;
    }
}


