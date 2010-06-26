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
Simple starter for stand-alone RESTx server.

"""
import os
import sys
import time
import getopt

# RESTx imports
import restx.settings as settings
import restx.logger   as logger

from restx.core                import RequestDispatcher
from restx.platform_specifics  import *

from org.mulesource.restx      import Settings
from org.mulesource.restx.util import Url

from org.mulesource.restx.component.api import *

def print_help():
    print \
"""
RESTx server (c) 2010 MuleSoft

Usage:  jython starter.py  [options]

Options:
        -h, --help
                Print this help screen.

        -P, --port <num>
                Port on which the server listens for requests.

        -p, --pidfile <filename>
                If specified, the PID of the server is stored in <filename>.

        -l, --logfile <filename>
                If specified, the filename for the logfile. If not specified,
                output will go to the console.

        -r, --rootdir <dirname>
                Root directory of the RESTx install
"""


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:P:p:r:", ["help", "logfile=", "port=", "pidfile=", "rootdir="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        print_help()
        sys.exit(1)

    port = settings.LISTEN_PORT
    for o, a in opts:
        if o in ("-p", "--pidfile"):
            # Writing our process ID
            pid = os.getpid()
            f = open(a, "w")
            f.write(str(pid))
            f.close()
        elif o in ("-h", "--help"):
            print_help()
            sys.exit(0)
        elif o in ("-P", "--port"):
            port = int(a)
        elif o in ("-r", "--rootdir"):
            rootdir = str(a)
            settings.set_root_dir(rootdir)
        elif o in ("-l", "--logfile"):
            logger.set_logfile(a)
            
    my_server = HttpServer(port, RequestDispatcher())

