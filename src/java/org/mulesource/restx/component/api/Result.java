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


package org.mulesource.restx.component.api;

import org.mulesource.restx.exception.*;

import java.util.HashMap;

/*
 * Inspired by the Result class defined for JAX-RS
 */
public class Result
{
    private int                     code;
    private Object                  data;
    private HashMap<String, String> headers;

    
    public Result(int code, Object data)
    {
        this.code    = code;
        this.data    = data;
        this.headers = null;
    }
    
    public void addHeader(String name, String value)
    {
        if (headers == null) {
            headers = new HashMap<String, String>();
        }
        headers.put(name, value);
    }
    
    public static Result ok()
    {
        return new Result(HTTP.OK, null);
    }
    
    public static Result ok(Object data)
    {
        return new Result(HTTP.OK, data);
    }
    
    public static Result created(String uri)
    {
        return created(uri, null);
    }
    
    public static Result created(String uri, Object obj)
    {
        Result res = new Result(HTTP.CREATED, obj);
        res.addHeader("Location", uri);
        return res;
    }
    
    public static Result notFound(String message)
    {
        return new Result(HTTP.NOT_FOUND, message);
    }
    
    public static Result badRequest(String message)
    {
        return new Result(HTTP.BAD_REQUEST, message);
    }
    
    public static Result noContent()
    {
        return new Result(HTTP.NO_CONTENT, null);
    }
    
    public static Result temporaryRedirect(String uri)
    {
        Result res = new Result(HTTP.TEMPORARY_REDIRECT, null);
        res.addHeader("Location", uri);
        return res;
    }
    
    public static Result internalServerError(String message)
    {
        return new Result(HTTP.INTERNAL_SERVER_ERROR, message);
    }
    
    public int getStatus()
    {
        return code;
    }
    
    public void setStatus(int code)
    {
        this.code = code;
    }
    
    public Object getEntity()
    {
        return data;
    }
    
    public void setEntity(Object data)
    {
        this.data = data;
    }
    
    public HashMap<String, String> getHeaders()
    {
        return headers;
    }
}



