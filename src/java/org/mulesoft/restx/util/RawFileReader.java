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

package org.mulesoft.restx.util;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

/*
 * This raw reader here is used when we read binary data. It's
 * easier to just write this code in Java than to try to deal
 * with implicit conversions when reading things in Python and
 * then passing it on to Java methods.
 */
public class RawFileReader
{
    public byte[] readFile(String fname) throws FileNotFoundException, IOException
    {
        int len = (int)(new File(fname).length());
        byte[] bb = new byte[len];
        FileInputStream fs = new FileInputStream(fname);
        fs.read(bb, 0, len);
        return bb;
    }
}


