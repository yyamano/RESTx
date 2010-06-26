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


class BaseRenderer(object):
    """
    Base class from which all renderers should derive.
    
    """
    def __init__(self, renderer_args):
        """
        The calling context can pass in some arguments
        to the renderer in form of a dictionary.
        
        @param renderer_args: Arguments to the renderer in form of a dictionary.
                              Some arguments only make sense for some types of renderers.
                              Other renderers will therefore just ignore arguments that
                              they don't know anything about.
        @type renderer_args:  dict
        
        """
        if renderer_args:
            self.renderer_args = renderer_args
        else:
            self.renderer_args = dict()
        
    def base_renderer(self, data, top_level=False):
        """
        Call the concrete render method of the child renderer.

        This method is here so that we can do some render-independent
        pre-processing of render-args.

        @param data:        An object containing the data to be rendered.
        @param data:        object
        
        @param top_level:   Flag indicating whether this we are at the
                            top level for output (this function is called
                            recursively and therefore may not always find
                            itself at the top level). This is important for
                            some renderers, since they can insert any framing
                            elements that might be required at the top level.
        @param top_level:   boolean
        
        @return:            Output buffer with completed representation.
        @rtype:             string

        """
        if self.renderer_args.get('raw'):
            # No special rendering, just plain output.
            return data
        else:
            return self.render(data, top_level)
        

    def render(self, data, top_level=False):
        """
        Take Python object and produce output specific to this renderer.
        
        @param data:        An object containing the data to be rendered.
        @param data:        object
        
        @param top_level:   Flag indicating whether this we are at the
                            top level for output (this function is called
                            recursively and therefore may not always find
                            itself at the top level). This is important for
                            some renderers, since they can insert any framing
                            elements that might be required at the top level.
        @param top_level:   boolean
        
        @return:            Output buffer with completed representation.
        @rtype:             string
        
        """    
        pass
    
