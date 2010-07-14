
#
# This little stub here allows you to test a component as
# standalone code.
#
import urllib
import restxjson as json

import profile

import restx.core

from restx.parameter                    import *
from restx.components.api               import *
from restx.components.base_capabilities import BaseCapabilities

#
# Import your component(s) here
#
from restx.components.TwitterComponent  import TwitterComponent as Component

# -----------------------------------------------------------------
# Don't edit the following...
#
c  = Component()
bc = BaseCapabilities(c)
c.setBaseCapabilities(bc)
#
# -----------------------------------------------------------------

#
# Write the test code for the component here.
#
# Start by assigning the resource creation time parameters
#

c.account_name     = "BrendelConsult"
c.account_password = "*********"

#
# Here we want to profile some code. So, we wrap the call to
# the component's service method into a simple function and
# then run this function through the profiler.
#
# However, you might think of any number of other things to
# do with the component, not just profiling...
#
def x():
    c.timeline("GET", None, 50, False)

profile.run("x()")

