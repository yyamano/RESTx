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
A sample template for RESTx components, written in Python.

"""
import urllib

from   restx.components.api   import *
import restx.settings         as     settings
import restx.components
from org.mulesource.restx.exception import *
from restx.resources          import makeResource 


class _ResourceCreateForm(BaseComponent):
    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "_ResourceCreateForm"    # Names starting with a '_' are kept private
    DESCRIPTION      = "Allows creation of a new resource by displaying a resource creation form"
    DOCUMENTATION    = \
"""The resource gets the name of a component as parameter at run time.
It then reads information about the component and constructs a proper
HTML form suitable for resource creation.

The user submits the filled-out form and a new resource is created.
"""

    PARAM_DEFINITION = {}
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           "form" : {
                               "desc" : "Show the resource creation form",
                               "params" : {
                                   "component_name" : ParameterDef(PARAM_STRING, "Name of the component", required=True),
                                   "message"        : ParameterDef(PARAM_STRING, "An error message", required=False, default=""),
                               },
                               "positional_params": [ "component_name" ]
                            },
                            "create" : {
                               "desc" : "Accepts a posted resource creation form",
                               "params" : {
                                   "component_name" : ParameterDef(PARAM_STRING, "Name of the component", required=True),
                               },
                               "positional_params": [ "component_name" ]
                           }
                       }
    
    def error_return(self, component_name, message):
        """
        Sends client back to form page with error message.

        """
        return Result.temporaryRedirect("%s/form/%s?message=%s" % (self.getMyResourceUri(), component_name, message))

    def create(self, method, input, component_name):
        """
        Accept a resource creation form for a specified component.

        """
        if not input:
            return self.error_return(component_name, "Need form input!")

        elems = input.split("&")
        d = dict()
        for e in elems:
            name, value = urllib.splitvalue(e)
            value = urllib.unquote_plus(value)
            path_elems = name.split("__")
            d2 = d
            for i, pe in enumerate(path_elems):
                if i < len(path_elems)-1:
                    # More elements to come later? We must create a dict
                    d2 = d2.setdefault(pe, dict())
                else:
                    if value:
                        d2[pe] = value
                    

        component_class = restx.components._CODE_MAP.get(component_name)
        try:
            ret_msg = makeResource(component_class, d)
        except RestxException, e:
            return self.error_return(component_name, e.msg)
        
        return Result.ok(ret_msg)

    def form(self, method, input, component_name, message=""):
        """
        Display a resource creation form for a specified component.
        
        @param method:          The HTTP request method.
        @type method:           string
        
        @param input:           Any data that came in the body of the request.
        @type input:            string

        @param component_name:  Name of the component for which to create the resource.
        @type component_name:   string

        @param message:         An error message to be displayed above the form.
        @type message:          string

        @return:                The output data of this service.
        @rtype:                 Result

        """
        cc = restx.components._CODE_MAP.get(component_name)
        if not cc:
            return Result.notFound("Cannot find component '%s'" % component_name)
        header = settings.HTML_HEADER

        # Assemble the form elements for the parameters
        params = dict()
        comp = cc()
        params.update(comp.getParams())  # In case this is a Java component, we get a Python dict this way
        param_fields_html = ""
        if params:
            for pname, pdef in params.items():
                if not pdef.required:
                    opt_str = "<br>optional, default: %s" % pdef.getDefaultVal()
                else:
                    opt_str = ""
                param_fields_html += \
"""<tr>
    <td valign=top>%s<br><small>(%s%s)</small></td>
    <td valign=top>%s</td>
</tr>""" % (pname, pdef.desc, opt_str, pdef.html_type("params__"+pname))

        if message:
            msg = "<b><i><font color=red>%s</font></i></b><br><p>" % message
        else:
            msg = ""

        body = """
<h3>Resource creation form for: %s</h3>
<p><i>"%s"</i></p>

<hr>
Please enter the resource configuration...<br><p>
%s
<form name="input" action="%s" method="POST">
    <table>
        <tr>
            <td>Resource name:</td>
            <td><input type="text" name="resource_creation_params__suggested_name" /></td>
        </tr>
        <tr>
            <td>Description:<br><small>(optional)</small></td>
            <td><input type="text" name="resource_creation_params__desc" /></td>
        </tr>
        %s
        <tr><td colspan=2 align=center><input type="submit" value="Submit" /></tr></tr>
    </table>
</form>""" % (comp.getName(), comp.getDesc(), msg, "%s/create/%s" % (self.getMyResourceUri(), component_name), param_fields_html)

        footer = settings.HTML_FOOTER

        res = Result.ok(header + body + footer)
        res.addHeader("Content-type", "text/html")

        return res

