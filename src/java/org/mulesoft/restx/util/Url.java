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

import org.mulesoft.restx.Settings;

public class Url
{
    private String urlStr;
    private String displayStr;
    
    public Url(String urlStr)
    {
        this(urlStr, null);
    }
    
    public Url(String urlStr, String displayStr)
    {
        // URIs that are within our server (starting with '/')
        // are prepended with the document root. That way, the
        // doc-root does not need to be referred to anywhere
        // else in the code, only in those places where we
        // render URIs.
        if (urlStr.charAt(0) == '/') {
            this.urlStr = Settings.DOCUMENT_ROOT + urlStr;
        }
        else {
            this.urlStr = urlStr;
        }
            
        if (displayStr == null) {
            this.displayStr = this.urlStr;
        }
        else {
            this.displayStr = displayStr;
        }
    }
    
    public String toString()
    {
        return urlStr;
    }

    public String as_html()
    {
        return "<a href=\"" + urlStr + "\">" + displayStr + "</a>";
    }
}


