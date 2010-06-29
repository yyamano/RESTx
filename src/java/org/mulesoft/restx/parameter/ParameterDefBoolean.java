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

public class ParameterDefBoolean extends ParameterDef
{
    private boolean defaultVal;
    
    public ParameterDefBoolean(String desc)
    {
        this(desc, true, false);
    }
        
    public ParameterDefBoolean(String desc, boolean defaultVal)
    {
        this(desc, false, defaultVal);
    }
    
    public ParameterDefBoolean(String desc, boolean required, boolean defaultVal)
    {
        super("boolean", desc, required);
        this.defaultVal = defaultVal;
    }

    @Override
    public Object getDefaultVal()
    {
        return defaultVal;
    }

    @Override
    public String html_type(String name)   // strange naming? This is called from Python code as well
    {
        String ret = "<label for=" + name + "_yes><input type=radio id="+name+"_yes name="+name+" value=yes />yes</label><br>";
        return ret + "<label for=" + name + "_no><input type=radio id="+name+"_no name="+name+" value=no />no</label><br>";
    }
}


