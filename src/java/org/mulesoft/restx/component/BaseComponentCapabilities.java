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


package org.mulesoft.restx.component;

import java.util.Map;

import org.mulesoft.restx.exception.RestxException;
import org.mulesoft.restx.util.JsonProcessor;
import org.mulesoft.restx.component.api.FileStore;
import org.mulesoft.restx.component.api.HttpResult;

public abstract class BaseComponentCapabilities
{
    // Storage
    public abstract FileStore  getFileStorage(String namespace);
    public          FileStore  getFileStorage()
    {
        return getFileStorage("");
    }

    // HTTP accesses
    public abstract void       httpSetCredentials(String accountName, String password);
    public abstract HttpResult httpGet(String url);
    public abstract HttpResult httpGet(String url, Map<String, String> headers);
    public abstract HttpResult httpPost(String url, String data);
    public abstract HttpResult httpPost(String url, String data, Map<String, String> headers);
}

