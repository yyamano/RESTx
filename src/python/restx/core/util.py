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
Utility definitions, methods and classes.

"""

'''
class Url(object):
    """
    Can be used like a string, but by having a dedicated
    type we can easily make better rendering decisions.
    
    This mostly used for the URIs when browsing code and
    resources, so that some of the renderes (specifically
    the HTML renderer) can show things in a convenient way
    to the user (clickable links).
    
    """
    def __init__(self, urlstr, display_str=None):
        """
        Initialize the URI class.
        
        @param urlstr:    The URI.
        @type urlstr:     string
        
        @param display_str:    The link text that should be displayed
                               to the user. If specified, the user may
                               get a clickable link with that text.
                               If it is not specified then the link text
                               will be the same as the URI itself.
        @type display_str:     string
        
        """                    
        self.urlstr = urlstr
        if display_str:
            self.display_str = display_str
        else:
            self.display_str = urlstr
    
    def __repr__(self):
        """
        Return the representation of the URI.
        
        @return:    Representation of the URI, in our case, just the string.
        @rtype:     string
        
        """
        return self.urlstr
    
    def __str__(self):
        """
        Return the string representation of the URI.
        
        @return:    The link as a string.
        @rtype:     string
        
        """
        return self.urlstr

    def as_html(self):
        """
        Return the URI properly rendered.
        
        The URI is surrounded by an <a href ...> tag.
        
        @return:    HTML representation of the URI.
        @rtype:     string
        
        """
        return '<a href="%s">%s</a>' % (self.urlstr, self.display_str)
'''

def bool_view(flag):
    """
    Translate a boolean value to a 'yes' or 'no' string.
    
    Use this function whenever showing a boolean value to the
    user. That way, we don't get the confusion on how to represent
    a flag to the user, which happens when you leave every developer
    to their own devices.
    
    @param flag:    Some boolean value.
    @type flag:     boolean
    
    @return:        "yes" or "no"
    @rtype:         string
    
    """
    return "yes" if flag else "no"


