#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright 2009 Lance Finn Helsten (helsten@acm.org)"""
__license__ = """
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
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

