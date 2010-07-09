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


import restxclient.api as restxapi

#server    = restxapi.RestxServer("http://localhost:8080/restx")   # For testing behind proxy
server    = restxapi.RestxServer("http://localhost:8001")         # For direct connection
component = server.get_component ("TestComponent")
print component.get_all_services()

print "\n\nAll services...\n\n"

for sname, sdef in component.get_all_services().items():
    print "@@@@ sname = ", sdef

print "\n\nOne service...\n\n"

srv = component.get_service("blahblah")
print "@@@@ src: ", srv

print "\n\nOne service...\n\n"

srv = component.get_service("foobar")
print "@@@@ src: ", srv

print "\n\nPositional parameters...\n\n"

print srv.get_positional_param_names()

print "\n\n-------------------------------------------\n\n"

print "\n\nAll resource names...\n\n"

print server.get_all_resource_names()


print "\n\nAll resource names PLUS...\n\n"


print server.get_all_resource_names_plus()


print "\n\nOne resource...\n\n"

r = server.get_resource("MyJavaTestComponent")
print r

print "\n\n--------------------------------------------\n\n"

rt = component.get_resource_template()
#rt.set("api_key", "foo")
rt.params         = dict(api_key="bar")
rt.description    = "Some description"
rt.suggested_name = "somename_p"

r = rt.create_resource()
print r
print r.get_all_services()
s = r.get_service("blahblah")
print s

print s.access()


print "\n\n--------------------------------------------\n\n"

status, data = server.get_resource("MyGoogleSearch").get_service("search").set("query", "mulesoft").access()

print data

r.delete()



 
