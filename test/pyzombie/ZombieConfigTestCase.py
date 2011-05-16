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

import sys
if sys.version_info < (3, 0):
    raise Exception("pyzombie requires Python 3.0 or higher.")
import unittest
import io
import pyzombie
from pyzombie.ZombieConfig import config



class ZombieConfigValuesTest(unittest.TestCase):    
    def runTest(self):
        self.assertEqual("localhost", config.get("pyzombie", "address"))
        self.assertEqual("8008", config.get("pyzombie", "port"))

        self.assertEqual("zombie", config.get("pyzombie_filesystem", "execbase"))
        self.assertEqual("image", config.get("pyzombie_filesystem", "binary"))

        self.assertEqual("./build/var/log/pyzombie", config.get("pyzombie_filesystem", "log"))
        self.assertEqual("./build/var/run/pyzombie.pid", config.get("pyzombie_filesystem", "run"))
        self.assertEqual("./build/var/data/pyzombie", config.get("pyzombie_filesystem", "data"))
        self.assertEqual("./build/var/cache/pyzombie", config.get("pyzombie_filesystem", "cache"))
        self.assertEqual("./build/var/spool/pyzombie", config.get("pyzombie_filesystem", "spool"))
