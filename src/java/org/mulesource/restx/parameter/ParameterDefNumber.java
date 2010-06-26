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


package org.mulesource.restx.parameter;

import java.math.BigDecimal;

public class ParameterDefNumber extends ParameterDef
{
    private BigDecimal defaultVal;
    
    public ParameterDefNumber(String desc)
    {
        this(desc, true, null);
    }
    
    public ParameterDefNumber(String desc, int defaultVal)
    {
        this(desc, false, defaultVal);
    }
        
    public ParameterDefNumber(String desc, float defaultVal)
    {
        this(desc, false, defaultVal);
    }
        
    public ParameterDefNumber(String desc, BigDecimal defaultVal)
    {
        this(desc, false, defaultVal);
    }
        
    public ParameterDefNumber(String desc, boolean required, int defaultVal)
    {
        this(desc, required, new BigDecimal(defaultVal));
    }
    
    public ParameterDefNumber(String desc, boolean required, float defaultVal)
    {
        this(desc, required, new BigDecimal(defaultVal));
    }
    
    public ParameterDefNumber(String desc, boolean required, BigDecimal defaultVal)
    {
        super("number", desc, required);
        this.defaultVal = defaultVal;
    }

    @Override
    public Object getDefaultVal()
    {
        return defaultVal;
    }
}


