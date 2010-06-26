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


package org.mulesource.restx.component;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.ArrayList;

import org.mulesource.restx.component.api.*;


@ComponentInfo(name        = "JavaTwitterComponent",
               description = "This is a Java implementation of a Twitter component",
               doc         = "The Twitter component is designed to provide access to a Twitter account." +
                             "It can be used to get status as well as update status.")
public class JavaTwitterComponent extends BaseComponent
{    
    @Parameter(name="account_name", desc="Twitter account name")
    public String account_name = null;
    
    @Parameter(name="account_password", desc="Password")
    public String account_password = null;

    private String getStatus()
    {
        HttpResult res = httpGet("http://api.twitter.com/1/users/show.json?screen_name=" + account_name);
        if (res.status == HTTP.OK) {
            return (String) res.data;
        }
        else {
            return "Problem with Twitter: " + res.data;
        }
    }
    
    private String postStatus(String data)
    {
        httpSetCredentials(account_name, account_password);
        HttpResult res = httpPost("http://api.twitter.com/1/statuses/update.xml", "status=" + data);
        return (String) res.data;
    }
    
    @Service(description = "You can GET the status or POST a new status to it.")
    public Result status(HttpMethod method, String input)
    {
        int    status = HTTP.OK;
        String data;
        if (method == HTTP.GET) {
            data = getStatus();
        }
        else {
            data = postStatus(input);
        }
        data = "Blah: " + input;
        return new Result(status, data);
        
    }
}


