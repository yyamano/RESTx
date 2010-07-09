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

from org.mulesoft.restx.clientapi import RestxServer
#server = RestxServer("http://localhost:8080/restx")   # For testing behind a proxy
server = RestxServer("http://localhost:8001")         # For direct connection



component = server.getComponent("TestComponent")
print component.getAllServices()

rt = component.getResourceTemplate()
rt.set("api_key", "bar")
rt.setDescription("Some description")
rt.setSuggestedName("somename")
r = rt.createResource()

print r.getAllServices()
s = r.getService("blahblah")
res = s.access()
print res.status
print res.data

r.delete()


