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

import java.util.HashMap;
import java.lang.Number;
import java.math.BigDecimal;

public class RestxParameter
{
    protected final static String   DESC_KEY       = "desc";
    protected final static String   REQ_KEY        = "required";
    protected final static String   TYPE_KEY       = "type";
    protected final static String   DEFAULT_KEY    = "default";

    protected final static String   PARAM_STRING   = "string";
    protected final static String   PARAM_PASSWORD = "password";
    protected final static String   PARAM_BOOL     = "boolean";
    protected final static String   PARAM_DATE     = "date";
    protected final static String   PARAM_TIME     = "time";
    protected final static String   PARAM_NUMBER   = "number";
    protected final static String   PARAM_URI      = "uri";
    
    protected final static String[] KNOWN_TYPES    = { PARAM_STRING, PARAM_PASSWORD, PARAM_BOOL,
                                                       PARAM_NUMBER, PARAM_URI };
    protected final static String[] REQUIRED_KEYS  = { DESC_KEY, REQ_KEY, TYPE_KEY };
    
    protected String                name;
    protected String                desc;
    protected boolean               required;
    protected String                typeStr;
    protected Object                defaultVal;
    
    /**
     * Take an object (either boolean or string) and return boolean value.
     * 
     * If the value is a string and is either "y", "yes", "t", "true" or "1"
     * then this returns 'true', otherwise 'false'
     * 
     * @param  val  An object to be interpreted as a boolean value, either
     *              a boolean or a string representation of a boolean.
     * @return      A boolean value.
     * 
     * @throws RestxClientException 
     */
    protected boolean boolConvert(Object val) throws RestxClientException
    {
        if (val == null) {
            return false;
        }
        if (val.getClass() == Boolean.class) {
            return ((Boolean)val).booleanValue();
        }
        else if (val.getClass() == String.class) {   
            String valStr = ((String)val).toLowerCase();
            if (valStr.equals("y")  ||  valStr.equals("yes")  ||  valStr.equals("t")  ||
                valStr.equals("true")  ||  valStr.equals("1"))
            {
                return true;
            }
            return false;
        }
        else {
            throw new RestxClientException("Cannot convert boolean.");
        }
    }
    
    /**
     * Convert an object (either a String or a Number) to a Number.
     * 
     * If the value is a string then we return BigDecimal. Otherwise, it
     * returns the value object itself.
     * 
     * @param  val  Either a Number object or a String representing a number. 
     * @return      The corresponding Number object, either Integer, Float,
     *              Double or BigDecimal.
     * @throws      RestxClientException
     */
    protected Object numstrToNum(Object val) throws RestxClientException
    {
        if (val == null  ||  Number.class.isInstance(val)) {
            return val;
        }
        else if (val.getClass() == String.class) {
            return new BigDecimal((String)val);
        }
        else {
            throw new RestxClientException("Cannot convert number.");
        }
    }
        
    /**
     * Convert an object to the specified type.
     * 
     * The type is specified as a string (one of our known types).
     * The function then attempts to take the object, which may
     * be a string or other type and convert it to the specified
     * type.
     * 
     * @param  val       A value object.
     * @param  typeName  The name of the type. Has to be from
     *                   our KNOWN_TYPES list.
     * @return           Either String, Integer, Boolean, Float,
     *                   Double or BigDecimal.
     * @throws RestxClientException 
     */
    protected Object typeConvert(Object val, String typeName) throws RestxClientException
    {
        if (typeName.equals(PARAM_STRING)  ||  typeName.equals(PARAM_PASSWORD)  ||  typeName.equals(PARAM_URI)) {
            if (val.getClass() == String.class) {
                return val;
            }
        }
        else if (typeName.equals(PARAM_BOOL)) {
            return boolConvert(val);
        }
        else if (typeName.equals(PARAM_NUMBER)) {
            return numstrToNum(val);
        }
        throw new RestxClientException("Type value mismatch for value '" + val + "' and type '" + typeName + "'.");
    }
    

    /**
     * Construct a new RestxParameter.
     * 
     * This takes a parameter definition hash map as they would be received
     * straight from the server. No prior sanity checking needs to be performed
     * on it, since this constructor properly parses and interprets this map.
     * 
     * @param  name  Name of the new parameter.
     * @param  pdef  HashMap describing the parameter definition.
     * 
     * @throws       RestxClientException
     */
    public RestxParameter(String name, HashMap<String, ?> pdef) throws RestxClientException
    {
        this.name = name;
        try {
            // Sanity check on received information
            RestxServer.checkKeyset(pdef, REQUIRED_KEYS);

            desc     = (String)pdef.get(DESC_KEY);
            required = boolConvert(pdef.get(REQ_KEY));
            typeStr  = (String)pdef.get(TYPE_KEY);
            
            boolean validTypeName = false;
            for (String knownName : KNOWN_TYPES) {
                if (knownName.equals(typeStr)) {
                    validTypeName = true;
                    break;
                }
            }
            if (!validTypeName) {
                throw new RestxClientException("Type '" + typeStr + "' specified for parameter '" + name + 
                                             "', which is not supported by this client library.");
            }
            
            if (!required) {
                Object defaultValRepr = pdef.get(DEFAULT_KEY);
                if (defaultValRepr == null) {
                    throw new RestxClientException("No default value specified for optional parameter '" + name + ".");
                }
                defaultVal = typeConvert(pdef.get(DEFAULT_KEY), typeStr);
            }
            else {
                if (!required) {
                    throw new RestxClientException("No default value specified for optional parameter '" + name + ".");
                }
                defaultVal = null;
            }
        }
        catch (RestxClientException e) {
            throw new RestxClientException("Malformed parameter definition: " + e.getMessage());
        }
    }
    
    /**
     * Used to check whether a proposed value object is of the right type for this parameter.
     * 
     * Returns nothing if all is well, otherwise throws exception.
     * 
     * @param  val  Value object.
     * @throws      RestxClientException
     */
    public void sanityCheck(Object val) throws RestxClientException
    {
        typeConvert(val, typeStr);
    }

    /**
     * Returns the name of the parameter.
     * 
     * @return  Name of parameter.
     */
    public String getName()
    {
        return name;
    }
    
    /**
     * Returns the description of the parameter.
     * 
     * @return  Description of the parameter.
     */
    public String getDescription()
    {
        return desc;
    }
    
    /**
     * Returns the string that was used to define the type.
     * 
     * This is one of the KNOWN_TYPES.
     * 
     * @return Type string for this parameter.
     */
    public String getParameterTypeStr()
    {
        return typeStr;
    }
    
    /**
     * Returns the object holding the default value for this parameter.
     * 
     * Might be null if no default value was set.
     * 
     * @return The default value object for this parameter.
     */
    public Object getDefaultValue()
    {
        return defaultVal;
    }
    
    /**
     * Returns the flag indicating whether this is a required parameter.
     * 
     * @return The required flag.
     */
    public boolean isRequired()
    {
        return required;
    }
}
