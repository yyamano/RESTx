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
    print "Usage: resource_use <server_url>"
    sys.exit(1)

url = sys.argv[1]

print "Connecting to server %s. Please wait..." % url
server = restxapi.RestxServer(url)
print "Ok. Connected."
resources = server.get_all_resource_names_plus()

print "\n=== Available resources ==="
names = [ name for name in resources.keys() ]
maxlen = 0
for n in names:
    if len(n) > maxlen:
        maxlen = len(n)
names.sort()
for i, n in enumerate(names):
    print "%3d. %s: %s" % (i+1, n.ljust(maxlen+1), resources[n]['desc'])

print "\n=== Which resource would you like to use? ==="
choice = input_num("Please enter resource number: ", 1, len(names))
res = server.get_resource(names[choice-1])
services = res.get_all_services()

print "\n=== Sub-resources of resource '%s' ===" % names[choice-1]
names = [ name for name in services.keys() ]
maxlen = 0
for n in names:
    if len(n) > maxlen:
        maxlen = len(n)
names.sort()
for i, n in enumerate(names):
    print "%3d. %s: %s" % (i+1, n.ljust(maxlen+1), services[n].get_description())

print "\n=== Which sub-resource would you like to use? ==="
choice = input_num("Please enter sub-resource number: ", 1, len(names))
service = services[names[choice-1]]
all_params = service.get_all_parameters()
if all_params:
    print "\n=== Please enter the values for all sub-resource parameters ==="
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

    service.params = pvals
else:
    print "(Sub-resource does not require parameters)"

print "\n=== Input for the sub-resource. Hit enter if no input is required or to end multi-line input:"
buf = ""
while True:
    inp = raw_input()
    if inp:
        buf += inp
    else:
        break
if buf:
    service.input = buf

print "\n=== Accessing sub-resource, please wait... ==="

status, data = service.access()
print "Server response code: ", status
print "Resturned data:       ", data

print "\n=== Done. ===\n"




