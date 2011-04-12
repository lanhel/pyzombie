#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
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
import socketserver
from .ZombieRequest import ZombieRequest
from .ZombieConfig import config, CONFIG_INIT

###
###
###
class ZombieServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Create a new ZombieServer to handle RESTful HTTP requests.
    
    This is built on `http.server.HTTPServer`_ so all HTTP requirements
    are handled correctly.
    
    :param configfile: Path to the server's configuration file.
    :param loglevel: The default log level for the new server.
    """
    def __init__(self):
        self.__init_makedir("log")
        self.__init_makedir("data")
        self.__init_makedir("cache")
        self.__init_makedir("spool")
        
        ### Start the server
        address = config.get("pyzombie", "address")
        port = int(config.get("pyzombie", "port"))
        super().__init__((address, port), ZombieRequest)

        ### Setup various properties
        self.maxagedynamic = config.get("pyzombie", "maxage_dynamic")
        self.maxagestatic = config.get("pyzombie", "maxage_static")
    
    def start(self):
        """Start the server."""
        try:
            sthread = threading.Thread(target=self.serve_forever)
            sthread.start()
            while (True):
                time.sleep(0.1)
        finally:
            self.shutdown()
    
    def __init_makedir(self, confname):
        """Make a directory given a named value in the config [filesystem] section."""
        path = config.get("pyzombie_filesystem", confname)
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            logging.getLogger().info("Create directory: {0}".format(path))
            os.makedirs(path)
        ## TODO: check permissions

