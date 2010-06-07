#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#$Id: setup.py 902 2009-10-16 16:38:28Z lance $
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server."""
__author__ = ('Lance Finn Helsten',)
__version__ = '0.0'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"

__all__ = ['ZombieServer']

import sys
import os
import io
import time
import threading
import configparser
from datetime import datetime
from datetime import timedelta
import logging
import logging.config
import http.client
import http.server
from .ZombieRequest import ZombieRequest

###
### Initial Configuration
###
CONFIG_INIT = """
[pyzombie]
address:        localhost
port:           8008
maxage_dynamic: 3600
maxage_static:  604800

[pyzombie_filesystem]
execbase:   zombie
binary:     executable

var=./build/var
log:        %(var)s/log/pyzombie
run:        %(var)s/run/pyzombie.pid
data:       %(var)s/data/pyzombie
cache:      %(var)s/cache/pyzombie
spool:      %(var)s/spool/pyzombie

[loggers]
keys=root,zombie

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_zombie]
level=DEBUG
handlers=consoleHandler
qualname=zombie
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s %(levelname)s %(message)s
datefmt=
"""



class ZombieServer(http.server.HTTPServer):
    def __init__(self, configfile, loglevel=logging.INFO):
        self.__init_config(configfile)
        self.__init_logging(loglevel)
        
        ### Start the server
        address = self.config.get("pyzombie", "address")
        port = int(self.config.get("pyzombie", "port"))
        super().__init__((address, port), ZombieRequest)

        ### Setup various properties
        self.stamp = datetime.utcnow()
        self.stamprfc850 = self.stamp.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.stampiso = self.stamp.isoformat()
        self.maxagedynamic = self.config.get("pyzombie", "maxage_dynamic")
        self.maxagestatic = self.config.get("pyzombie", "maxage_static")
    
    def start(self):
        try:
            sthread = threading.Thread(target=self.serve_forever)
            sthread.start()
            while (True):
                time.sleep(0.1)
        finally:
            self.shutdown()
    
    def __init_config(self, configfile):
        self.configfile = configfile
        self.config = configparser.SafeConfigParser()
        self.config.readfp(io.StringIO(CONFIG_INIT))
        if os.path.isfile(self.configfile):
            print("Configuration:", configfile)
            self.config.read(configfile)
    
    
    def __init_logging(self, loglevel):
        try:
            logging.config.fileConfig(self.configfile)
        except configparser.NoSectionError:
            print("Using default logging configuration.")
            logging.config.fileConfig(io.StringIO(CONFIG_INIT))
            logging.getLogger("zombie").setLevel(loglevel)
        logging.getLogger().info("Hello World")
    
    
    def __init_filesystem(self):
        self.__init_makedir("log")
        self.__init_makedir("data")
        self.__init_makedir("cache")
        self.__init_makedir("spool")
    
    
    def __init_makedir(confname):
        """Make a directory given a named value in the config [filesystem] section."""
        path = self.config.get("pyzombie_filesystem", confname)
        path = os.path.normpath(path)
        print(path)
        if not os.path.isdir(path):
            os.makedirs(path)
        ## TODO: check permissions

