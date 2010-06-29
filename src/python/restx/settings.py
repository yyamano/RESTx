"""
RESTx: Sane, simple and effective data publishing and integration. 

Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version. 

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details. 

You should have received a copy of the GNU General Public License 
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""

"""
Settings for RESTx.

"""

DOCUMENT_ROOT   = "/"
PREFIX_META     = "/meta"
PREFIX_CODE     = "/code"
PREFIX_RESOURCE = "/resource"
PREFIX_STATIC   = "/static"

LISTEN_PORT     = 8001

STATIC_LOCATION     = "static_files/"
RESOURCEDB_LOCATION = "resourceDB/"
STORAGEDB_LOCATION  = "storageDB/"
CONF_LOCATION       = "conf/"
ROOT_DIR            = ""

DOC_FILE_NAME       = "DOC"
VERSION_FILE_NAME   = "VERSION"

__VERSION = None

def get_version():
    global __VERSION
    if not __VERSION:
        f = open(get_root_dir() + CONF_LOCATION + VERSION_FILE_NAME, "r")
        __VERSION = f.readline().strip()
        f.close()
    return __VERSION

def get_docs():
    f = open(get_root_dir() + CONF_LOCATION + DOC_FILE_NAME, "r")
    buf = ''.join(f.readlines())
    f.close()
    return buf

def set_root_dir(rootdir):
    global ROOT_DIR
    if not rootdir.endswith("/"):
        rootdir += "/"
    ROOT_DIR = rootdir

def get_root_dir():
    return ROOT_DIR

NEVER_HUMAN   = False

HTML_HEADER = """
<html>
    <head>
        <title>MuleSoft RESTx</title>

        <style type="text/css"> 
        
            p {
                color:#000;
            }
            
            h1 {
                font-weight:bold;
                font-size:2em;
            }
            
            h2 {
                font-weight:bold;
                font-size:1.5em;;
            }
        
            hr {
                height: 1px;
                background:#bbb;
                margin:20px 0px;
            }
        
            table {
                border: 1px solid #fff;
                color:#222;
            }

            td.dict {
                padding:2px 4px;
                background-color:#e5e6e3;
                border: 1px solid #fff;
                color:#aaa;
            }

            td.key {
                padding:2px 4px;
                background-color:#f3f4f2;
                border: 1px solid #fff;
                color:#334;
            }
            
            td {
                padding:2px 4px;
                background-color:#f3f4f2;
                border: 1px solid #fff;
            }
            
            a { 
                color: #016C96; 
            }

            body {
                font-family:Helvetica, Arial, Verdana, sans-serif;
                color:#222;
                font-size:1em;
            }
                
            a:link, a:visited, a:active {
                text-decoration: none; 
            }
            
            a:hover { 
                text-decoration: underline; 
            }

            span.string {
                font-family:Times, "Times New Roman", serif;
                font-style:italic;
            }
        </style> 

    </head>
    <body>
        <a target="_blank" href="http://restx.mulesoft.org"><img style="padding-right:10px" width="97" height="30" src="/static/restx/images/restx_logo.png" alt="RESTx" /></a>
        <i>The fastest and easiest way to create RESTful resources</i>
        <hr>
"""

HTML_FOOTER = """
<hr>
<center><a target="_blank" href="http://mulesoft.com"><img src="/static/restx/images/logo-mule-s.png" alt="MuleSoft" /></a></center>
</body>
</html>
"""
