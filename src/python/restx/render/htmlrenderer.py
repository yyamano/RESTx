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
Contains the HTML-renderer class.

"""
# Python imports
from copy   import copy
import string

# RESTx imports
import restx.settings as settings

from restx.render.baserenderer import BaseRenderer
from restx.core.util           import bool_view

from org.mulesource.restx.util import Url

class HtmlRenderer(BaseRenderer):
    """
    Outputs Python objects into HTML.
    
    Understands the renderer_args:
    
        * no_annotations (no writing of 'List' or 'Object' before lists or dicts)
        * no_table_headers (no writing of 'Key' and 'Value' above dictionaries)
        * no_list_indices (no writing of array indices)
        * no_border (no table and cell borders)
    
    """
    CONTENT_TYPE = "text/html"

    def __init__(self, renderer_args, breadcrumbs, context_header=None):
        """
        Initialize the renderer.
        
        @param renderer_args:  A dictionary of flags, which can influence the
                               output. The flags are explained in the class docstring.
        @type renderer_args:   dict
        
        @param breadcrumbs:    The breadcrumbs for this request. Defined as a list
                               of (name,uri) tuples, for navigation. Breadcrumbs are
                               maintained by the browser class for this request.
        @type breadcrumbs:     list

        @param context_header: Additional headers or menus, which are to be displayed
                               under some circumstances. Example: The 'create' menu
                               item, which is shown when a component is viewed.
        @type context_header:  list
        
        """
        super(HtmlRenderer, self).__init__(renderer_args)
        self.draw_annotations = False if self.renderer_args.get('no_annotations') else True
        self.table_headers    = False if self.renderer_args.get('no_table_headers') else True
        self.draw_indices     = False if self.renderer_args.get('no_list_indices') else True
        self.draw_borders, self.border_width = (False,0) if self.renderer_args.get('no_borders') else (True,1)
        self.breadcrumbs      = breadcrumbs
        self.context_header   = context_header
        
        self.header = settings.HTML_HEADER + \
                      '%s<br><hr>' % (self.__render_breadcrumbs(self.breadcrumbs))
        if context_header:
            self.header += ' &nbsp; '.join(['<a %s href="%s">%s</a><br>' % (options, uri, name) for (name, uri, options) in context_header ])
            self.header += "<br>"
                      
                      
    def __render_breadcrumbs(self, breadcrumbs):
        """
        Output HTML for breadcrumbs.
        
        Breadcrumbs are given as a list of tuples, with each tuple containing
        a (name,URI). The last breadcrumb should not be rendered as a clickable
        link.
        
        @param breadcrumbs:   List of breadcrumbs.
        @type breadcrumbs:    list
        
        @return:              HTML for breadcrumbs.
        @rtype:               string
        
        """
        segments = []
        for i, elem in enumerate(breadcrumbs):
            name, uri = elem
            if i < len(breadcrumbs)-1:
                # All but the last element are rendered as clickable links
                segments.append('<a href="%s">%s</a>' % (uri, name))
            else:
                segments.append(name)
        return " > ".join(segments)            
            
    def __dict_render(self, data):
        """
        Take Python dictionary and produce HTML output.
        
        The output of a dictionary is modified by some of the renderer arguments.
        
        @param data:    A dictionary that needs to be rendered in HTML.
        @type  data:    dict
        
        @return:        HTML representation of the dictionary.
        @rtype:         string        
        """
        annotation   = "<i>Object</i><br/>\n" if self.draw_annotations else ""

        keys = copy(data.keys())
        # In the future we might want to display particular items
        # in specific positions, but for now, we just sort the
        # items alphabetically.
        keys.sort()
        out = "%s<table border=%d cellspacing=0>\n" % (annotation, self.border_width)
        if self.table_headers:
            # For the time being, we won't render table headers, since they look a
            # bit clunky. If we want them to go back in, just uncomment this line.
            #out += '<tr><td class="dict"><i>Key</i></td><td class="dict"><i>Value</i></td></tr>\n'
            pass
        for key in keys:
            out += '<tr>\n<td class="key" valign=top>%s</td>\n<td valign=top>' % \
                                            (key.as_html() if type(key) is Url else key)
            out += self.render(data[key])
            out += "\n</td>\n</tr>"
        out += "</table>"
        return out
    
    def __list_render(self, data):
        """
        Take Python list and produce HTML output.
        
        The output of a list is modified by some of the renderer arguments.
        
        @param data:    A list that needs to be rendered in HTML.
        @type  data:    list
        
        @return:        HTML representation of the list.
        @rtype:         string
        
        """
        annotation   = "<i>List</i><br/>\n" if self.draw_annotations else ""
        out = "%s<table border=%d cellspacing=0>" % (annotation, self.border_width)
        for i, elem in enumerate(data):
            if self.draw_indices:
                index_column = "<td valign=top>%d</td>" % i
            else:
                index_column = ""
            out += "<tr>%s<td valign=top>%s</td></tr>" % (index_column, self.render(elem))
        out += "</table>"
        return out
    
    def __plain_render(self, data):
        """
        Take a non-list, non-dict Python object and produce HTML.
        
        A simple conversion to string is performed.
        
        @param data:    A Python object
        @type  data:    object
        
        @return:        HTML representation of the object.
        @rtype:         string

        """
        if type(data) is unicode  or  type(data) is str:
            # WSGI wants str(), but some unicode characters can cause exceptions.
            # I'm sure there are better ways to do this, but that works for now.
            # When we use Jython then we can get unprintable characters even
            # in str (while later string operations may fail, which is totally
            # odd...)
            data = ''.join([ (str(x) if x in string.printable else "") for x in data ])
        # Note that when we use Jython we still have unicode (the conversion to str
        # doesn't seeem to work). That's why in the following line we have to test
        # for str() as well as unicode(). The return in unicode is not a problem
        # for the Java server.
        if type(data) is str  or  type(data) is unicode:
            if data.startswith("http://") or data.startswith("https://")  or data.startswith("/"):
                data = Url(data)
        if data is None:
            out = "---"
        elif type(data) is Url:
            out = data.as_html()
        elif type(data) is bool:
            out = bool_view(data)
        else:
            if type(data) is not unicode:
                data_str = str(data)
            else:
                data_str = data
            if type(data) is not str  and  type(data) is not unicode  and  type(data) in [ int, float ]:
                # Output as number
                out = data_str
            else:
                #out = '<i>%s</i>' % data_str.replace("\n", "<br/>")
                #out = '<span class="string">%s</span>' % data_str
                # This is HTML rendering, so we want to give even normal text to preserve
                # some of its formatting. A simple way to do that is to replace double \n
                # with a single <br>. Triple \n is replaced with two <br> tags, resulting
                # in the rendering of an empty line.
                # This simple strategy allows us to preserve paragraph breaks and formatting
                # without markup, which would be a nuisance in a plain text representation.
                data_str = data_str.replace("\n\n\n", "<br/><br/>")
                out = '<span class="string">%s</span>' % data_str.replace("\n\n", "<br/>")
        return out

    def render(self, data, top_level=False):
        """
        Take Python object and produce HTML output.
        
        @param data:        An object containing the data to be rendered.
        @param data:        object
        
        @param top_level:   Flag indicating whether this we are at the
                            top level for output (this function is called
                            recursively and therefore may not always find
                            itself at the top level). This is important for
                            some renderers, since they can insert any framing
                            elements that might be required at the top level.
                            In the case of this HTML renderer, we can add
                            some nice headers and footers.
        @param top_level:   boolean
        
        @return:            Output buffer with completed representation.
        @rtype:             string
            
        """
        out = ""
        if type(data) is dict:
            out += self.__dict_render(data)
        elif type(data) is list:
            out += self.__list_render(data)
        else:
            out += self.__plain_render(data)
        if top_level:
            out = "%s%s%s" % (self.header, out, settings.HTML_FOOTER)
        return out
