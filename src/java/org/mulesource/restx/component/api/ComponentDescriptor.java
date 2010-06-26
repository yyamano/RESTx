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

import java.util.HashMap;

import org.mulesource.restx.exception.RestxException;
import org.mulesource.restx.exception.RestxDuplicateKeyException;
import org.mulesource.restx.parameter.ParameterDef;

public class ComponentDescriptor
{
    /*
     * This descriptor is assembled by the component to provide the
     * meta data description about itself to the RESTx framework.
     */
    private String name;
    private String descriptionText;
    private String docText;
    
    private HashMap<String, ParameterDef>      params;
    private HashMap<String, ServiceDescriptor> services;
    
    public ComponentDescriptor(String name, String descriptionText, String docText)
    {
        this.name            = name;
        this.descriptionText = descriptionText;
        this.docText         = docText;
        this.params          = new HashMap<String, ParameterDef>();
        this.services        = new HashMap<String, ServiceDescriptor>();
    }
    
    /*
     * Add a new parameter to the list of params. If one with that
     * name exists already then it is just overwritten.
     */
    public void addParameter(String name, ParameterDef pdef) throws RestxDuplicateKeyException
    {
        if (params.containsKey(name)) {
            throw new RestxDuplicateKeyException("Parameter '" + name + "' already exists.");
        }
        
        params.put(name, pdef);
    }
    
    public void addService(String name, ServiceDescriptor service) throws RestxDuplicateKeyException
    {
        if (services.containsKey(name)) {
            throw new RestxDuplicateKeyException("Service '" + name + "' already exists.");
        }
        
        services.put(name, service);
    }
    
    public HashMap<String, ParameterDef> getParamMap()
    {
        return params;
    }
    
    public HashMap<String, ServiceDescriptor> getServicMap()
    {
        return services;
    }
    
    public String getName()
    {
        return name;
    }
    
    public String getDesc()
    {
        return descriptionText;
    }
    
    public String getDocs()
    {
        return docText;
    }
    
    /*
     * Internally, services are stored as a plain dictionary (because that's how
     * it was done in Python). Therefore, we provide this method here to return
     * a plain-dict representation of the assembled service description.
     */
    public HashMap<String, Object> getServicesAsPlainDict()
    {
        HashMap<String, Object> servicesDict = new HashMap<String, Object>();
        
        for (String name: services.keySet()) {
            ServiceDescriptor service = services.get(name);
            HashMap<String, Object> serviceDef = new HashMap<String, Object>();
            servicesDict.put(name, serviceDef);
            serviceDef.put("desc", service.getDesc());
            serviceDef.put("params", service.getParamMap());
            if (!service.getPositionalParams().isEmpty()) {
                serviceDef.put("positional_params", service.getPositionalParams());
            }
        }
        
        return servicesDict;
    }
}


