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


package org.mulesoft.restx.component.api;

public class HTTP
{
    public static final HttpMethod GET               = HttpMethod.GET;
    public static final HttpMethod POST              = HttpMethod.POST;
    public static final HttpMethod PUT               = HttpMethod.PUT;
    public static final HttpMethod DELETE            = HttpMethod.DELETE;
    public static final HttpMethod HEAD              = HttpMethod.HEAD;
    public static final HttpMethod OPTIONS           = HttpMethod.OPTIONS;

    public static final String     GET_METHOD        = "GET";
    public static final String     POST_METHOD       = "POST";
    public static final String     PUT_METHOD        = "PUT";
    public static final String     DELETE_METHOD     = "DELETE";
    public static final String     HEAD_METHOD       = "HEAD";
    public static final String     OPTIONS_METHOD    = "OPTIONS";

    public static final int CONTINUE                          = 100;
    public static final int SWITCHING_PROTOCOLS               = 101;
    public static final int OK                                = 200;
    public static final int CREATED                           = 201;
    public static final int ACCEPTED                          = 202;
    public static final int NON_AUTHORITIVE                   = 203;
    public static final int NO_CONTENT                        = 204;
    public static final int RESET_CONTENT                     = 205;
    public static final int PARTIAL_CONTENT                   = 206;
    public static final int MULTIPLE_CHOICES                  = 300;
    public static final int MOVED_PERMANENTLY                 = 301;
    public static final int FOUND                             = 302;
    public static final int SEE_OTHER                         = 303;
    public static final int NOT_MODIFIED                      = 304;
    public static final int USE_PROXY                         = 305;
    public static final int TEMPORARY_REDIRECT                = 307;
    public static final int BAD_REQUEST                       = 400;
    public static final int UNAUTHORIZED                      = 401;
    public static final int PAYMENT_REQUIRED                  = 402;
    public static final int FORBIDDEN                         = 403;
    public static final int NOT_FOUND                         = 404;
    public static final int METHOD_NOT_ALLOWED                = 405;
    public static final int NOT_ACCEPTABLE                    = 406;
    public static final int PROXY_AUTHENTICATION_REQUIRED     = 407;
    public static final int REQUEST_TIMEOUT                   = 408;
    public static final int CONFLICT                          = 409;
    public static final int GONE                              = 410;
    public static final int LENGTH_REQUIRED                   = 411;
    public static final int PRECONDITION_FAILED               = 412;
    public static final int REQUEST_ENTITY_TOO_LARGE          = 413;
    public static final int REQUEST_URI_TOO_LONG              = 414;
    public static final int UNSUPPORTED_MEDIA_TYPE            = 415;
    public static final int REQUEST_RANGE_NOT_SATISFIED       = 416;
    public static final int EXPECTATION_FAILED                = 417;
    public static final int INTERNAL_SERVER_ERROR             = 500;
    public static final int NOT_IMPLEMENTED                   = 501;
    public static final int BAD_GATEWAY                       = 502;
    public static final int SERVICE_UNAVAILABLE               = 503;
    public static final int GATEWAY_TIMEOUT                   = 504;
    public static final int VERSION_NOT_SUPPORTED             = 505;

}


