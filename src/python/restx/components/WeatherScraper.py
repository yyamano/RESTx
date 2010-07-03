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
A component that can scrape weather information from Web pages

"""
# Imports all aspects of the API
from restx.components.api import *

#
# We use BeautifulSoup for parsing of HTML pages.
# This can be installed with 'jython $JYTHON_HOME/bin/easy_install beautifulsoup'
#
from BeautifulSoup import BeautifulSoup
import re

# -------------------------------------------------------
# A RESTx component needs to be derived from BaseComponent.
# -------------------------------------------------------
class WeatherScraper(BaseComponent):

    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "WeatherScraper"
    DESCRIPTION      = "A component that can scrape weather information from Web pages"
    DOCUMENTATION    = \
"""
This component can scrape weather data from a web page.


The scraping function is still quite primitive. You need
to be able to identify the information with a few particular
tags that we can search for.


For example, assume the temperature is surrounded by a certain
&lt;div&gt; tag, like so:
<pre>
    &lt;div unit="metric" class="ccTemp"&gt;22 degrees&lt;div&gt;
</pre>
Then you can specify as the 'temp_tag':
<pre>
    &lt;div class="ccTemp"&gt;
</pre>
The weather scraper will find the matching tag and extract
the content. If there is markup within the content it is removed.
For example, if the page contains:
<pre>
    &lt;div unit="metric" class="ccTemp"&gt;&lt;b&gt;22 degrees&lt;b&gt;&lt;div&gt;
</pre>
Then the "&lt;b&gt;" and "&lt;/b&gt;" tags are removed.


Because the HTML parsing process is a tad slow, you should only
work on a subset of the overall page content. For that, give a
a unique starting text that you can expect to find in the page
somewhere just before the section that contains the current
weather conditions, plus a maximum number of characters after
the start of that text.


Oftentimes, a suitable start text is a surrounding div for the
current information. For example:
<pre>
    &lt;div id="currentConditions"&gt;
</pre>
Since the current conditions are usually relatively close on a
page, you should be fine setting a 'search_length' of around
10000 or so.

"""

    # Resource creation time parameters.
    # Each parameter is created through a ParameterDef object, which encapsulates
    # the definition of the parameter. The PARAM_* argument determines the type
    # of the parameter. Currently, we know PARAM_STRING, PARAM_NUMBER and PARAM_BOOL.
    PARAM_DEFINITION = {
                           "url"               : ParameterDef(PARAM_STRING,
                                                              "The URL of the page from which to scrape the content.",
                                                              required=True),
                           "unique_start_text" : ParameterDef(PARAM_STRING,
                                                              "Define a unique text from where to start the search from. If ommitted, search starts from the beginning.",
                                                              required=False, default=""),
                           "search_length"     : ParameterDef(PARAM_NUMBER,
                                                              "How many characters of text are searched from the specified start. If ommitted, we will search to the end.",
                                                              required=False, default=-1),
                           "temp_tag"          : ParameterDef(PARAM_STRING,
                                                              "The tag on the page, which surrounds the temperature.",
                                                              required=False, default=""),
                           "wind_tag"          : ParameterDef(PARAM_STRING,
                                                              "The tag on the page, which surrounds information about the wind information.",
                                                              required=False, default=""),
                           "condition_tag"     : ParameterDef(PARAM_STRING,
                                                              "The tag on the page, which surrounds wheather condition information.",
                                                              required=False, default=""),
                        }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           "current" : {
                               "desc" : "Provide current weather information",
                           }
                       }
        

    __PATTERN = None    # A cache for a compiled regular expression


    def _bsearch(self, otag):
        """
        Helper method: Needed for proper search with BeautifulSoup.

        Convert a tag like this:

            <div class="foo bar">

        to two values:

            "div"
            { "class" : "foo bar" }

        """
        #
        # Check, but then strip the surrounding '< ... >' brackets.
        #
        if not otag.startswith("<")  or  not otag.endswith(">"):
            raise RestxBadRequestException("Tag not specified correctly.")
        otag = otag[1:-1]

        #
        # Don't need to compile the pattern every time. We cache it once
        # it has been created for the first time.
        #
        if not self.__PATTERN:
            self.__PATTERN = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')

        #
        # Let the regex work its magic. It correctly detects quotes
        # and does NOT split on spaces within a quoted string.
        # Borrowed from Duncan's answer (Thank you!) I found on StackOverflow:
        # http://stackoverflow.com/questions/2785755/how-to-split-but-ignore-separators-in-quoted-strings-in-python
        #
        elems = self.__PATTERN.split(otag)[1::2]

        #
        # First element is the tag name ('div', 'span', etc.)
        #
        tagname  = elems[0]

        #
        # Remaining tags are assembled into a dictionary,
        # so we can pass that as keyword-args into the find()
        # function of BeautifulSoup. Since we are talking about
        # tag attributes here, the tag-name and attribute value
        # can be separated just by splitting along '='. If there
        # are strange attributes without '=' then we just ignore
        # those (catch and ignore exception).
        #
        attrdict = dict()
        for e in elems[1:]:
            try:
                name, value = e.split("=")
                attrdict[str(name)] = value.strip('"')
            except:
                pass

        return tagname, attrdict

    
    def _markup_remover(self, buf):
        """
        Helper method: Remove any annoying markup, which could impact the formatting.

        """
        buf = buf.replace("<br>", "").replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "").replace("<br/>", "").replace("\n", "")
        buf = buf.replace("\n", "").replace("<", "<! ")
        return buf


    def current(self, method, input):
        """
        Service method to extract the current weather information from a page.

        This is driven by the tags, which were specified during resource
        creation time.

        We currently only extract three items of information.

            - Temperature
            - Current condition
            - Wind

        """

        #
        # Load HTML of the web page that contains the weather info
        #
        (status, data) = self.httpGet(self.url)

        #
        # Find the unique start text, which allows us to skip over
        # HTML at the start of the page. Especially for longer
        # pages it's really important to skip over unnecessary
        # stuff, since the parsing can be CPU intensive.
        #
        if self.unique_start_text:
            start_index = data.find(self.unique_start_text)
            if start_index < 0:
                start_index = 0
        else:
            start_index = 0

        #
        # Determine the end of text we should search, so that we
        # can skip more stuff at the end. Most weather pages will
        # have the current information relatively close together,
        # so specifying 10000 as search_length will usually be
        # a good choice.
        #
        if self.search_length > 0:
            end_index = start_index + self.search_length
        else:
            end_index = len(data)

        #
        # Get the region of HTML that we are interested in and
        # give it to BeautifulSoup for parsing.
        #
        sdata = data[start_index:end_index]
        soup  = BeautifulSoup(sdata)


        #
        # A small helper method, which uses BeautifulSoup's
        # find() method to search for the specific tag.
        # The content we find is then stripped of any remaining
        # markup tags.
        #
        def extract(tag):
            if tag:
                tagname, attrs = self._bsearch(tag)
                p = soup.find(tagname, **attrs)
                if not p:
                    return "Currently not available"
                else:
                    return self._markup_remover(p.renderContents())
            else:
                return "Not available"
            
        #
        # Get temperature info from page and assemble
        # result dictionary.
        #
        result = dict()
        result["Temperature"] = extract(self.temp_tag)
        result["Condition"]   = extract(self.condition_tag)
        result["Wind"]        = extract(self.wind_tag)

        return Result.ok(result)


