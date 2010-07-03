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

/**
 * Only used here to hold description and URIs of
 * components and resources.
 * 
 * When we query /code or /resource on the server, we
 * get back a dictionary of dictionaries. The second-
 * level dictionaries don't hold the full information
 * about a component or resource, but just the name
 * and URI. This class here represents that.  
 */
public class DescUriHolder
{
    public String desc;
    public String uri;
    
    /**
     * Construct a new description holder.
     * 
     * @param desc   Description of the element.
     * @param uri    URI of the element.
     */
    public DescUriHolder(String desc, String uri)
    {
        this.desc = desc;
        this.uri  = uri;
    }
}
