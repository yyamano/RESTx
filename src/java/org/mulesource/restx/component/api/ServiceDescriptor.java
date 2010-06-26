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

import java.util.ArrayList;
import java.util.HashMap;

import org.mulesource.restx.exception.RestxDuplicateKeyException;
import org.mulesource.restx.exception.RestxMalformedServiceDescriptorException;
import org.mulesource.restx.parameter.ParameterDef;

public class ServiceDescriptor
{
    /*
     * Defines a single service for a resource.
     */
    private String desc;
    
    private HashMap<String, ParameterDef> params;
    private ArrayList<String>             positionalParams;

    public ServiceDescriptor(String desc)
    {
        this.desc             = desc;
        this.params           = new HashMap<String, ParameterDef>();
        this.positionalParams = new ArrayList<String>();
    }
    
    public String getDesc()
    {
        return desc;
    }
    
    public void addParameter(String name, ParameterDef param) throws RestxDuplicateKeyException
    {
        if (params.containsKey(name)) {
            throw new RestxDuplicateKeyException("Parameter '" + name + "' already exists.");
        }
        
        params.put(name, param);
    }
    
    public HashMap<String, ParameterDef> getParamMap()
    {
        return params;
    }
    
    public void setPositionalParameters(ArrayList<String> positionals) throws RestxMalformedServiceDescriptorException
    {
        for (String name : positionals) {
            if (!params.containsKey(name)) {
                throw new RestxMalformedServiceDescriptorException("Parameter '" + name + "' from positionals does not exist");
            }
        }
        
        for (String elem: positionals) {
            positionalParams.add(elem);
        }
    }
    
    public ArrayList<String> getPositionalParams()
    {
        return positionalParams;
    }
}

