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
import os
import io
import shutil
import unittest
import pyzombie
from pyzombie.Executable import Executable
from pyzombie.ZombieConfig import config, datadir


class ExecutableBase(unittest.TestCase):
    def setUp(self):
        self.ex = Executable(self.__class__.__name__, mediatype="text/x-python")

    def tearDown(self):
        self.ex.delete()


class ExecutablePropertiesTest(ExecutableBase):
    """Check that properties are correctly initialized."""
    def runTest(self):
        self.assertEqual(datadir(), self.ex.datadir)
        self.assertEqual(config.get("pyzombie_filesystem", "execbase"), self.ex.execbase)
        self.assertEqual(config.get("pyzombie_filesystem", "binary"), self.ex.binaryname)
        self.assertEqual(self.__class__.__name__, self.ex.name)
        self.assertEqual(os.path.join(datadir(), self.__class__.__name__), self.ex.dirpath)
        self.assertEqual(os.path.join(datadir(), self.__class__.__name__, self.ex.binaryname + ".py"), self.ex.binpath)
        self.assertEqual(("text/x-python", None), self.ex.mediatype)
    

class ExecutableIOTest(ExecutableBase):
    """Check that the executable image is correctly saved."""
    def runTest(self):
        val = "Hello world"
        buf = io.StringIO()
        self.ex.writeimage(io.StringIO(val))
        self.ex.readimage(buf)
        self.assertEqual(val, buf.getvalue())


