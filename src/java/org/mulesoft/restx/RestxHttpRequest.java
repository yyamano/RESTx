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


package org.mulesoft.restx;

import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;

public abstract class RestxHttpRequest
{
    /*
     * This is the base class we use for our HttpRequest.
     * By using a Java base class, we can use the HttpRequest
     * equally easily in Java as well as Python.
     */
    public abstract void    setNativeMode();       // Subsequently returned dictionaries are in native (Java) form
    public abstract void    setNativeRequest(HttpExchange nativeRequest);
    public abstract void    setResponseCode(int code);
    public abstract void    setResponseBody(String body);
    public abstract void    setResponseHeader(String name, String value);
    public abstract void    setResponse(int code, String body);
    public abstract String  getRequestProtocol();
    public abstract String  getRequestMethod();
    public abstract String  getRequestURI();
    public abstract String  getRequest();
    public abstract Headers getRequestHeaders();   // We return a dict() for Python. Python doesn't care.
    public abstract String  getRequestQuery();
    public abstract String  getRequestBody();
    public abstract void    sendResponseHeaders();
    public abstract void    sendResponseBody();
    public abstract void    sendResponse();
    public abstract void    close();    
}


