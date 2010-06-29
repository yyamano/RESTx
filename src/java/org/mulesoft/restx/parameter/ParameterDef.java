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


package org.mulesoft.restx.parameter;

import java.util.HashMap;

public abstract class ParameterDef
{
    public String  ptype;
    public String  desc;
    public boolean required;
    
    public ParameterDef(String ptype, String desc, boolean required)
    {
        this.ptype    = ptype;
        this.desc     = desc;
        this.required = required;
    }
    
    public abstract Object getDefaultVal();
    
    public HashMap<String, Object> asDict()
    {
        HashMap<String, Object> d = new HashMap<String, Object>();
        
        d.put("type",     ptype);
        d.put("desc",     desc);
        d.put("required", required);
        d.put("default",  getDefaultVal());
        
        return d;
    }

    public String html_type(String name)   // strange naming? This is called from Python code as well
    {
        return "<input type=text name="+name+" />";
    }

}


