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


import sys
import urllib
import restxclient.api as restxapi



def input_num(prompt, min, max):
    while True:
        try:
            choice = int(raw_input(prompt))
        except:
            print "*** Enter a valid number! Please try again..."
            continue
        if choice < min  or  choice > max:
            print "*** Number out of range. Please try again..."
            continue
        return choice



print sys.argv
if len(sys.argv) != 2:
    print "Usage: resource_maker <server_url>"
    sys.exit(1)

url = sys.argv[1]

print "Connecting to server %s. Please wait..." % url
server = restxapi.RestxServer(url)
print "Ok. Connected."
components = server.get_all_component_names_plus()

print "\n=== Available components ==="
names = [ name for name in components.keys() ]
maxlen = 0
for n in names:
    if len(n) > maxlen:
        maxlen = len(n)

names.sort()
for i, n in enumerate(names):
    print "%3d. %s: %s" % (i+1, n.ljust(maxlen+1), components[n]['desc'])

print "\n=== For which component would you like to create a resource? ==="
choice = input_num("Please enter component number: ", 1, len(names))

i = choice-1
cname = names[i]
print "\n=== Creating resource for %s component ===" % cname
component = server.get_component(cname)
if not component:
    print "Cannot receive component!"
    sys.exit(1)
print "Ok. Component info received."

rt = component.get_resource_template()
all_params = rt.get_all_parameters()
print "\n=== Please enter the values for all resource-creation time parameters ==="
pvals = dict()
for name in all_params:
    param = all_params[name]
    print "Parameter '%s':" % name
    print "    Type:       ", param.get_parameter_type_str()
    print "    Desc:       ", param.get_description()
    print "    Required:   ", param.is_required()
    if not param.is_required():
        msg = " (leave blank to accept default value)"
        print "    Default:   ", param.get_default_value() 
    else:
        msg = ""

    print
    while True:
        inp = raw_input("    Enter value%s: " % msg)
        if not inp:
            if param.is_required():
                print "*** A value is required for this parameter. Please try again..."
                continue
        else:
            try:
                param.sanity_check(inp)
            except:
                print "*** This input cannot successfully be converted to the required type. Please try again..."
                continue
            pvals[name] = inp
        print
        break

rt.params = pvals

while True:
    name = raw_input("Suggested name for resource: ")
    if not name:
        print "*** Please enter a suggested name for the new resource."
        continue
    qname = urllib.quote(name)
    if qname != name:
        print "*** Name contains URL un-safe characters. Please try a different name..."
        continue
    try:
        r_existing = server.get_resource(name)
        print "*** A resource with that name exists already. Please try a different name..."
        continue
    except:
        pass
    break

desc_default = component.get_resource_description().get_default_value()
desc = raw_input("Description for resource (enter for default '%s'): " % desc_default)
if not desc:
    desc = desc_default

rt.description    = desc
rt.suggested_name = name

print "\n=== Attempting to create new resource on the server ==="
r = rt.create_resource()
print "\n=== Resource successfully created! ===\n"

print r, "\n"


