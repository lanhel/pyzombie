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
