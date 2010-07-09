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

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.HttpURLConnection;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;


/**
 * Used by the client to encapsulate all communication with the server.
 * 
 * When created, some meta information from the server is read and stored.
 * This object also serves as a cache for often accessed information.
 */
public class RestxServer
{
    // The well-known URIs where we can find specific server information
    protected static final String            CODE_URI_KEY     = "code";
    protected static final String            DOC_URI_KEY      = "doc";
    protected static final String            NAME_KEY         = "name";
    protected static final String            RESOURCE_URI_KEY = "resource";
    protected static final String            STATIC_URI_KEY   = "static";
    protected static final String            VERSION_KEY      = "version";
    protected static final String            META_URI         = "/";
    protected static final String            DESCURI_DESC_KEY = "desc";
    protected static final String            DESCURI_URI_KEY  = "uri";
    
    protected static final String[]          REQUIRED_KEYS    = { CODE_URI_KEY, DOC_URI_KEY, NAME_KEY,
                                                                  RESOURCE_URI_KEY, STATIC_URI_KEY,
                                                                  VERSION_KEY };

    protected HashMap<String, String>        DEFAULT_REQ_HEADERS;
    protected String                         serverUri;
    protected String                         componentUri;
    protected String                         docUri;
    protected String                         docRoot;
    protected String                         name;
    protected String                         resourceUri;
    protected String                         staticUri;
    protected String                         doc;
    protected String                         version;
    protected HashMap<String, DescUriHolder> resources;
    protected HashMap<String, DescUriHolder> components;

    /**
     * Used to send requests to the server.
     * 
     * The right headers are assembled and a suitable HTTP method will be selected if
     * not specified by the caller.
     * 
     * @param url     The URL on the server to which the request should be sent. Since
     *                this relies on an established server connection, the URL here is
     *                just the path component of the URL (including possible query
     *                parameters), starting with '/'.
     * @param data    Any data we want to send with the request (in case of PUT or POST).
     *                If data is specified, but no method is given, then the method will
     *                default to POST. If a method is specified as well then it must be
     *                POST or PUT. If no data should be sent then this should be 'null'.
     * @param method  The desired HTTP method of the request.
     * @param status  The expected status. If the HTTP status from the server is
     *                different than the expected status, an exception will be thrown. If
     *                no status check should be performed then set this to 'null'.
     * @param headers A {@link HashMap<String, String>} in which any additional
     *                request headers should be specified. For example: { "Accept" :
     *                "application/json" }. The hash map will not be modified by this
     *                method.
     *                
     * @return        A {@link HttpResult} object with status and data that was returned by
     *                the server.
     *                
     * @throws        RestxClientException
     */
    public HttpResult send(String url,
                           String data,
                           HttpMethod method,
                           Integer status,
                           HashMap<String, String> headers) throws RestxClientException
    {
        // Set default values for the method if nothing was specified. Depends on
        // whether we want to send data or not.
        if (method == null) {
            if (data == null) {
                method = HttpMethod.GET;
            }
            else {
                method = HttpMethod.POST;
            }
        }

        // Combine default headers with any additional headers
        if (headers == null) {
            headers = DEFAULT_REQ_HEADERS;
        }
        else {
            HashMap<String, String> hm = new HashMap<String, String>(headers);
            for (String name : DEFAULT_REQ_HEADERS.keySet()) {
                hm.put(name, DEFAULT_REQ_HEADERS.get(name));
            }
            headers = hm;
        }

        URL               fullUrl = null;
        HttpURLConnection conn    = null;

        try {
            if (!url.startsWith("/")) {
                url = "/" + url;
            }
            fullUrl = new URL(serverUri + url);
            conn    = (HttpURLConnection) fullUrl.openConnection();

            // Set the request headers
            for (String name : headers.keySet()) {
                conn.setRequestProperty(name, headers.get(name));
            }

            // Set the request method
            conn.setRequestMethod(HttpMethod.toString(method));

            // Send the message body
            if (data != null) {
                conn.setDoOutput(true);
                OutputStreamWriter wr = new OutputStreamWriter(conn.getOutputStream());
                wr.write(data);
                wr.flush();
            }

            // Get the response
            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String line;
            StringBuffer buf = new StringBuffer();
            while ((line = rd.readLine()) != null) {
                // For now we do nothing particularly efficient. We just assemble all
                // the data we get into a big string.
                buf.append(line);
            }
            rd.close();

            int respStatus = conn.getResponseCode();

            if (status != null) {
                if (status != respStatus) {
                    throw new RestxClientException("Status code " + status + " was expected for request to '" +
                                                 fullUrl + "'. Instead we received " + respStatus);
                }
            }
            return new HttpResult(conn.getResponseCode(), buf.toString());
        }
        catch (Exception e) {
            if (conn != null) {
                // This exception was thrown after we started to connect to the server
                int    code;
                String msg;
                
                try {
                    // We may even have an initialised response already, in which case
                    // we are passing that information back to the caller.
                    code = conn.getResponseCode();
                    msg  = conn.getResponseMessage();
                }
                catch (IOException e1) {
                    // The problem occurred before the response status in the HTTP
                    // connection was initialised.
                    code = HttpURLConnection.HTTP_INTERNAL_ERROR;
                    msg  = e.getMessage();
                }
                if (status != null) {
                    if (status != code) {
                        throw new RestxClientException("Status code " + status + " was expected for request to '" +
                                                       fullUrl + "'. Instead we received " + code);
                    }
                }
                return new HttpResult(code, msg);
            }
            // The exception was thrown before we even initialised our connection
            throw new RestxClientException("Cannot connect with URI '" + fullUrl +
                                         "': " + e.getMessage());
        }
    }

    /**
     * Serialize a complex object to JSON.
     * 
     * We should be able to just use {@link JSONObject} for all kinds of objects.
     * However, it does not handle strings, numbers or booleans, only maps or arrays.
     * Therefore, we deal with those manually.
     * 
     * @param  obj The object to be serialized. The object has to be a string, number
     *             or boolean, or a HashMap and/or ArrayList consisting of those basic
     *             types or further HashMaps and ArrayLists.
     *             
     * @return     The JSON string representation of the object.
     * 
     * @throws     RestxClientException
     */
    public static String jsonSerialize(Object obj) throws RestxClientException
    {
        try {
            Class oclass = obj.getClass();
            if (oclass == Map.class) {
                // The JSON library offers a specific class for maps...
                return (new JSONObject(obj)).toString();
            }
            else if (oclass == Collection.class) {
                // ... and another for arrays.
                return (new JSONArray(obj)).toString();
            }
            else {
                // But all other (normal) types are different. For some reason
                // the JSON library doesn't seem to handle this well.
                // So, we solve the issue by putting this other type of object
                // into a list, use JSONArray(), convert to string and strip off
                // the leading and trailing '[' and ']'. Then we have the proper
                // JSON-stype string representation of that type, which we can
                // return. This is extremely kludgy. One of these days we might
                // 
                ArrayList al = new ArrayList();
                al.add(obj);
                String buf = (new JSONArray(al)).toString();
                return buf.substring(1, buf.length() - 1);
            }
        }
        catch (JSONException e) {
            throw new RestxClientException("Could not serialize data: " + e.getMessage());
        }
    }

    /**
     * Transcribes a JSONObject into a HashMap.
     * 
     * Just a small helper method.
     * 
     * @param   obj Instance of {@link JSONObject}.
     * @return      A string representing the JSON serialization.
     * @throws      JSONException
     */
    protected static HashMap jsonObjectTranscribe(JSONObject obj) throws JSONException
    {
        HashMap  d         = new HashMap();
        String[] nameArray = JSONObject.getNames(obj);
        if (nameArray != null) {
            for (String name : JSONObject.getNames(obj)) {
                Object o = obj.get(name);
                if (o.getClass() == JSONArray.class) {
                    o = jsonListTranscribe((JSONArray) o);
                }
                else if (o.getClass() == JSONObject.class) {
                    o = jsonObjectTranscribe((JSONObject) o);
                }
                d.put(name, o);
            }
        }
        return d;
    }

    /**
     * Transcribes a JSONArray object into an ArrayList object.
     * 
     * Just a small helper method.
     * 
     * @param  arr A {@link JSONArray} instance.
     * @return     A string representing the JSON serialization.
     * @throws     JSONException
     */
    protected static ArrayList jsonListTranscribe(JSONArray arr) throws JSONException
    {
        ArrayList l = new ArrayList();
        for (int i = 0; i < arr.length(); ++i) {
            Object o = arr.get(i);
            if (o.getClass() == JSONArray.class) {
                o = jsonListTranscribe((JSONArray) o);
            }
            else if (o.getClass() == JSONObject.class) {
                o = jsonObjectTranscribe((JSONObject) o);
            }
            l.add(o);
        }
        return l;
    }

    /**
     * Deserializes a JSON string into a complex object.
     * 
     * @param  str A JSON string, representing a complex object.
     * 
     * @return     A complex object, which will be a string, number or boolean, or a
     *             HashMap or ArrayList containing any of the other types.
     *             
     * @throws     RestxClientException
     */
    public static Object jsonDeserialize(String str) throws RestxClientException
    {
        try {
            JSONTokener t = new JSONTokener(str);
            Object      v = t.nextValue();
            if (v.getClass() == JSONArray.class) {
                v = jsonListTranscribe((JSONArray) v);
            }
            else if (v.getClass() == JSONObject.class) {
                v = jsonObjectTranscribe((JSONObject) v);
            }
            return v;
        }
        catch (JSONException e) {
            throw new RestxClientException("Could not de-serialize data: " + e.getMessage());
        }
    }

    /**
     * Send and receive complex, JSON serialized objects.
     * 
     * This is a wrapper around {@link send}, which serializes complex objects to
     * JSON strings and assume that the response can equally be de-serialized from JSON.
     * 
     * @param url     The URL on the server to which the request should be sent. Since
     *                this relies on an established server connection, the URL here is
     *                just the path component of the URL (including possible query
     *                parameters), starting with '/'.
     *                
     * @param data    Any data we want to send with the request (in case of PUT or POST).
     *                If data is specified, but no method is given, then the method will
     *                default to POST. If a method is specified as well then it must be
     *                POST or PUT. If no data should be sent then this should be 'null'.
     *                This is assumed to be a complex object, which will be JSON
     *                serialized before sending.
     *                
     * @param method  The desired HTTP method of the request.
     * 
     * @param status  The expected status. If the HTTP status from the server is
     *                different than the expected status, an exception will be thrown. If
     *                no status check should be performed then set this to 'null'.
     *            
     * @param headers A {@link HashMap<String, String>} in which any additional
     *                request headers should be specified. For example: { "Accept" :
     *                "application/json" }. The hash map will not be modified by this
     *                method.
     *                
     * @return        A {@link HttpResult} object with status and data that was returned by
     *                the server. The data is a complex object, which was de-serialized from
     *                the JSON string that was received from the server.
     *                
     * @throws        RestxClientException
     */
    public HttpResult jsonSend(String url,
                               Object data,
                               HttpMethod method,
                               Integer status,
                               HashMap<String, String> headers) throws RestxClientException
    {
        String dataStr;
        // We need to add a few custom headers. Since we don't want to
        // modify the header map that was passed to us (the caller might
        // want to use it a few more times), we will make a copy and add
        // our stuff into that.
        HashMap<String, String> newHeaders = null;
        if (headers == null) {
            newHeaders = new HashMap<String, String>();
        }
        else {
            newHeaders = new HashMap<String, String>(headers);
        }
        newHeaders.put("Accept", "application/json");

        if (data != null) {
            // Serialise data via JSON
            dataStr = jsonSerialize(data);
            // Tell the recipient about our content type. We make a new
            newHeaders.put("Content-type", "application/json");
        }
        else {
            dataStr = null;
        }
        HttpResult res = send(url, dataStr, method, status, headers);
        res.data = jsonDeserialize((String) res.data); // / JSON de-serialized
        return res;
    }
    
    
    /**
     * Returns description and URI for each resource or component.
     * 
     * An overview of resources and components can be had via the same
     * sort of structure: A dictionary that maps their names to a brief
     * summary, consisting of description and URI for each resource or
     * component.
     * 
     * @param  uri   The URI from which to retrieve this information.
     * @return       A map consisting of DescUriHolder objects.
     * @throws       RestxClientException
     */
    protected HashMap<String, DescUriHolder> getDescUriMap(String uri) throws RestxClientException
    {
        HttpResult                res = jsonSend(uri, null, null, 200, null);
        HashMap<String, HashMap>  hm  = (HashMap<String, HashMap>)res.data;
        
        // Store the dictionary we get from the server in a hash map
        // that uses the DescUriHolder class.
        HashMap<String, DescUriHolder> data = new HashMap<String, DescUriHolder>();
        for (String name: hm.keySet()) {
            HashMap<String, String> elem = hm.get(name);
            DescUriHolder           duh  = new DescUriHolder(elem.get(DESCURI_DESC_KEY),
                                                             elem.get(DESCURI_URI_KEY));
            data.put(name, duh);
        }
        return data;
    }

    /*******************************************************************
     * Public server interface
     *******************************************************************/

    /**
     * Useful utility method, which checks whether a map contains all required keys.
     * 
     * Throws an exception if not all required keys are present.
     * 
     * @param  hm            Map to check for required keys.
     * @param  requiredKeys  List of required keys.
     * 
     * @throws               RestxClientException 
     */
    public static void checkKeyset(HashMap hm, String[] requiredKeys) throws RestxClientException
    {
        for (String name : requiredKeys) {
            if (!hm.containsKey(name)) {
                throw new RestxClientException("Missing expected key '" + name + ".");
            }
        }
    }
    
    /**
     * Create a new client-side representation of a RestxServer.
     * 
     * A request is sent for the server's meta data information. Some basic sanity
     * checking is performed on the received data.
     * 
     * @param serverUri The absolute URI at which the server can be found. For
     *                  example: "http://localhost:8001".
     *                  
     * @throws          MalformedURLException
     * 
     * @throws          RestxClientException
     */
    public RestxServer(String serverUri) throws MalformedURLException, RestxClientException
    {
        // Don't need any trailing '/'
        int i = serverUri.length()-1;
        
        while (i > 0  &&  serverUri.charAt(i) == '/') {
            --i;
        }
        if (i>0) {
            serverUri = serverUri.substring(0, i+1);
        }
        else {
            throw new MalformedURLException();
        }
        
        this.serverUri = serverUri;
        DEFAULT_REQ_HEADERS = new HashMap<String, String>();
        DEFAULT_REQ_HEADERS.put("Accept", "application/json");

        URL url = new URL(serverUri);

        // Some sanity checking on the URI.
        this.serverUri = url.getProtocol() + "://" + url.getHost();
        if (url.getPort() > -1) {
            this.serverUri += ":" + Integer.toString(url.getPort());
        }

        if (!url.getPath().isEmpty()) {
            docRoot = url.getPath();
        }
        else {
            docRoot = "";
        }

        if (!url.getProtocol().equals("http")) {
            throw new RestxClientException("Only 'http' schema is currently supported.");
        }

        // Receive server meta data
        HttpResult              res = jsonSend(docRoot + META_URI, null, HttpMethod.GET, 200, null);
        HashMap<String, String> hm  = (HashMap<String, String>)res.data;

        // Sanity check on received information
        try {
            checkKeyset(hm, REQUIRED_KEYS);
        }
        catch (RestxClientException e) {
            throw new RestxClientException("Server error: Malformed server meta data: " + e.getMessage());
        }

        // Store the meta data for later use
        try {
            componentUri = hm.get(CODE_URI_KEY);
            docUri       = hm.get(DOC_URI_KEY);
            name         = hm.get(NAME_KEY);
            resourceUri  = hm.get(RESOURCE_URI_KEY);
            staticUri    = hm.get(STATIC_URI_KEY);
            version      = hm.get(VERSION_KEY);
        }
        catch (Exception e) {
            throw new RestxClientException("Malformed server meta data: " + e.getMessage());
        }
        
        doc        = null;
        resources  = null;
        components = null;
    }
    
    /**
     * Sends the request to create a new resource on the server.
     * 
     * Clients don't use this method, but instead create a resource
     * through a {@link RestxResourceTemplate} object.
     * 
     * @param  uri   The full URI (starting with a '/') of the component.
     * 
     * @param  rdict The dictionary with all required parameters for the
     *               resource creation.
     *               
     * @return       An HttpResult object, containing the response from the server.
     * 
     * @throws       RestxClientException
     */
    protected HashMap<String, Object> createResource(String uri, Object rdict) throws RestxClientException
    {
        HttpResult res = jsonSend(uri, rdict, null, 201, null);
        return (HashMap<String, Object>) res.data;
    }
    
    /**
     * Return the URI of the server to which we are connected.
     * 
     * @return  The full server URI, as it was specified when the
     *          RestxServer object was created.
     */
    public String getServerUri()
    {
        return serverUri;
    }
    
    /**
     * Return the version string of the server to which we are connected.
     * 
     * @return  The version string of the server.
     */
    public String getServerVersion()
    {
        return version;
    }
    
    /**
     * Returns the name of the server.
     * 
     * The 'name' is a token that was returned by the server when we connected
     * to it for the first time. Each server can be configured with its own
     * name. However, the URI of the server should actually be sufficient to
     * differentiate amongst them.
     * 
     * @return  Name of the server.
     */
    public String getServerName()
    {
        return name;
    }
    
    /**
     * Return the doc page for the server.
     * 
     * If we don't have a copy of it already then we issue a request to
     * the server to retrieve the doc information.
     * 
     * @return A string containing the server documentation.
     * @throws RestxClientException
     */
    public String getServerDoc() throws RestxClientException
    {
        if (doc == null) {
            HttpResult res = jsonSend(docUri, null, null, 200, null);
            doc = (String)res.data;
        }
        return doc;
    }

    /**
     * Return high level information about all resources currently known on the server.
     * 
     * This retrieves a map from the server, which contains description and URI for
     * each resource.
     * 
     * @return  Map with information about each resource.
     * @throws  RestxClientException
     */
    public HashMap<String, DescUriHolder> getAllResourceNamesPlus() throws RestxClientException
    {
        resources = getDescUriMap(resourceUri);
        return resources;
    }

    /**
     * Return the names of all resources currently known on the server.
     * 
     * @return  Names of all resources.
     * @throws  RestxClientException
     */
    public String[] getAllResourceNames() throws RestxClientException
    {
        // Refresh the resource list.
        getAllResourceNamesPlus();

        // Jump through hoops to get the hash-map keys as a String[],
        // because we can't just do a simple cast on the array.
        Object[] ks       = resources.keySet().toArray();
        String[] strArray = new String[ks.length];        
        System.arraycopy(ks, 0, strArray, 0, ks.length);
        return strArray;
    }
    
    /**
     * Return high level information about all components currently known on the server.
     * 
     * This retrieves a map from the server, which contains description and URI for
     * each component.
     * 
     * @return  Map with information about each component.
     * @throws  RestxClientException
     */
    public HashMap<String, DescUriHolder> getAllComponentNamesPlus() throws RestxClientException
    {
        components = getDescUriMap(componentUri);
        return components;
    }

    /**
     * Return the names of all components currently known on the server.
     * 
     * @return  Names of all components.
     * @throws  RestxClientException
     */
    public String[] getAllComponentNames() throws RestxClientException
    {
        // Refresh the component list.
        getAllComponentNamesPlus();

        // Jump through hoops to get the hash-map keys as a String[],
        // because we can't just do a simple cast on the array.
        Object[] ks       = components.keySet().toArray();
        String[] strArray = new String[ks.length];        
        System.arraycopy(ks, 0, strArray, 0, ks.length);
        return strArray;
    }
    
    /**
     * Return an initialized {@link RestxComponent} object for the specified component.
     * 
     * @param  name   Name of the component.
     * @return        Initialized {@link RestxComponent} object.
     * @throws        RestxClientException 
     */
    public RestxComponent getComponent(String name) throws RestxClientException
    {
        HttpResult res = jsonSend(componentUri+"/"+name, null, null, 200, null);
        // The data of the HTTP result should be a dictionary with the component info
        return new RestxComponent(this, (HashMap)res.data);
    }
    
    /**
     * Return an initialized {@link RestxResource} object for the specified resource.
     * 
     * @param  name   Name of the resource.
     * @return        Initialized {@link RestxResource} object.
     * @throws        RestxClientException 
     */
    public RestxResource getResource(String name) throws RestxClientException
    {
        HttpResult res = jsonSend(resourceUri+"/"+name, null, null, 200, null);
        // The data of the HTTP result should be a dictionary with the component info
        return new RestxResource(this, (HashMap)res.data);        
    }
}
