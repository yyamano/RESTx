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


package org.mulesource.restx;

import org.python.util.PythonInterpreter;
import org.python.core.PyObject;
import org.python.core.PyString;

public class Settings
{
    /*
     * Eventually this will provide access to all config parameters.
     * In the meantime, it uses some Jython specifics to get access to
     * the configs that are stored in settings.py
     */
    
    /*
     * Our handle on the Python interpreter. It is initialized in the static
     * initializer and then re-used in the getFromPythonSettings() method.
     */
    private static PythonInterpreter interp;

    /*
     * Used to initialize individual Java class members with values from
     * the Python settings.py module.
     */
    private static String getFromPythonSettings(String objName)
    {
        PyObject pyObject = interp.get(objName);
        return (String)pyObject.__tojava__(String.class);        
    }
    
    /*
     * Initialize and import only once.
     */
    static {
        interp = new PythonInterpreter();
        interp.exec("from restx.settings import *");
    }

    /*
     * Here finally we have the publicly exported symbols.
     */
    public static String PREFIX_CODE     = getFromPythonSettings("PREFIX_CODE");
    public static String PREFIX_RESOURCE = getFromPythonSettings("PREFIX_RESOURCE");;
}


