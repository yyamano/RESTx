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
Logger functions.

We don't use native Python or Java logging, since we want
to use this here as an abstraction around whatever logging
infrastructure we will have in our finished system.

"""
import sys
import datetime


# Log levels
LOG_DEBUG       = "DEBUG"
LOG_INFO        = "INFO"
LOG_WARNING     = "WARNING"
LOG_ERROR       = "ERROR"
LOG_CRITICAL    = "CRITICAL"

# Log facilities
LOGF_RESTX_CORE   = "RESTX_CORE"
LOGF_ACCESS_LOG = "ACCESS_LOG"
LOGF_RESOURCES  = "RESOURCES"
LOGF_COMPONENTS = "COMPONENTS"

__KNOWN_LEVELS     = [ LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR, LOG_CRITICAL ]
__KNOWN_FACILITIES = [ LOGF_RESTX_CORE, LOGF_ACCESS_LOG, LOGF_RESOURCES, LOGF_COMPONENTS ]

_LOGFILE=None

def set_logfile(logfile=None):
    global _LOGFILE
    _LOGFILE=logfile

def log(msg, level=LOG_INFO, facility=LOGF_RESTX_CORE, start_time=None):
    """
    Log a message with specified log level and facility.
    
    @param msg:        The log message.
    @type  msg:        string
    
    @param level:      The log level.
    @type  level:      string
    
    @param facility:   The system facility from which the message was produced.
    @type  facility:   string
    
    @param start_time: The time at which processing of this request started.
    @type  start_time: datetime
    
    """
    if level not in __KNOWN_LEVELS  or  facility not in __KNOWN_FACILITIES:
        msg = "### Invalid level (%s) or facility (%s). Original message: %s" % (level, facility, msg)
        level    = LOG_INFO
        facility = LOGF_RESTX_CORE
    if not start_time:
        start_time = datetime.datetime.now()
    timestring = start_time.isoformat()
    if facility == LOGF_ACCESS_LOG:
        facility_level = LOGF_ACCESS_LOG
    else:
        facility_level = "%s:%s" % (facility, level)
    outstr = "### %s - %s - %s\n" % (timestring, facility_level, msg)
    if not _LOGFILE:
        sys.stderr.write(outstr)
    else:
        f = open(_LOGFILE, "a+")
        f.write(outstr)
        f.close()


