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


package org.mulesoft.restx.component;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;

import org.mulesoft.restx.component.api.*;
import org.mulesoft.restx.exception.*;


@ComponentInfo(name        = "TestComponent",
               description = "This is a Java test component",
               doc         = "Here is a doc string")
public class TestComponent extends BaseComponent
{    
    @Parameter(name="api_key", desc="This is the API key")
    //@Default("foo foo foo")
    public String api_key;
    
    @Service(description = "This is the foobar service")
    public Result foobar(HttpMethod method, String input,
                         
                         @Parameter(name="query", desc="This is the query string", positional=true)
                         @Default("foo")
                         String     query,
                         
                         @Parameter(name="num", desc="The number of results", positional=true)
                         @Default("10")
                         BigDecimal num)
    {
        System.out.println("----------------------------------------------------------");
        System.out.println("### input:   " + input.getClass() + " === " + input);
        System.out.println("### method:  " + method.getClass() + " === " + method);
             
        System.out.println("Query parameter: " + query);
        System.out.println("Num parameter:   " + num);
        
        HashMap res = new HashMap();
        res.put("foo", "This is a test");
        HashMap sub = new HashMap();
        res.put("bar", sub);
        sub.put("some value", 1);
        sub.put("another value", "Some text");
        ArrayList v = new ArrayList();
        v.add("Blah");
        v.add(12345);
        sub.put("some ArrayList", v);
        
        v = new ArrayList();
        v.add("Some text");
        v.add(123);
        v.add(res);
        
        return Result.ok(v);
    }
 
    @Service(description = "Makes another resource")
    public Result maker(HttpMethod method, String input) throws RestxException
    {
        HashMap params = new HashMap();
        params.put("api_key", "123123");
        params.put("default_search", "java");

        MakeResourceResult res = makeResource("GoogleSearchComponent", "NewResourceName", "Description for my resource", params);
        String resbuf = "Created a resource! Status: " + res.status + " --- Name: " + res.name + " --- URI: " + res.uri;
        return Result.ok(resbuf);
    }

    @Service(description = "This accesses a Python Google search resource and returns the result")
    public Result blahblah(HttpMethod method, String input)
    {
        HttpResult res;
        HashMap params = new HashMap();
        params.put("query", "foo");
        res = accessResource("/resource/MyGoogleSearch/search", null, params);
        return new Result(res.status, res.data);
    }
}


