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
Exports the various components, which are available.

Also defines a base class for all components.

"""
# Import all the components
import restx_components_list

#
# Assemble list of the known components
#
_KNOWN_COMPONENTS = [ getattr(restx_components_list, name) for name in dir(restx_components_list) if not name.startswith("__") ]
_CODE_MAP = dict([ (component_class().getName(), component_class) for component_class in _KNOWN_COMPONENTS ])

