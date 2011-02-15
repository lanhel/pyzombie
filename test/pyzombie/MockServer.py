#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie mock server."""
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

import sys
import os
import io
import datetime
import configparser
import http.client
from pyzombie.ZombieServer import CONFIG_INIT

class MockServer():
    
    def __init__(self):
        self.config = configparser.SafeConfigParser()
        self.config.readfp(io.StringIO(CONFIG_INIT))
        
        self.stamp = datetime.datetime(1966, 8, 29, 11, 53, 22, 435123)
        self.stamprfc850 = self.stamp.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.stampiso = self.stamp.isoformat()
        self.maxagedynamic = self.config.get("pyzombie", "maxage_dynamic")
        self.maxagestatic = self.config.get("pyzombie", "maxage_static")

    @property
    def server_name(self):
        return "MockServer"
    
    @property
    def server_port(self):
        return 8008