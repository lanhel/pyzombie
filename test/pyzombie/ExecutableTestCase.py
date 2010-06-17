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
        self.ex = Executable("testexec", mediatype="text/x-python")

    def tearDown(self):
        shutil.rmtree(self.ex.dirpath)


class ExecutablePropertiesTest(ExecutableBase):

    def runTest(self):
        self.assertEqual(datadir(), self.ex.datadir)
        self.assertEqual(config.get("pyzombie_filesystem", "execbase"), self.ex.execbase)
        self.assertEqual(config.get("pyzombie_filesystem", "binary"), self.ex.binaryname)
        self.assertEqual("testexec", self.ex.name)
        self.assertEqual(os.path.join(datadir(), "testexec"), self.ex.dirpath)
        self.assertEqual(os.path.join(datadir(), "testexec", self.ex.binaryname + ".py"), self.ex.binpath)
        self.assertEqual(("text/x-python", None), self.ex.mediatype)
    

class ExecutableIOTest(ExecutableBase):
    def runTest(self):
        val = "Hello world"
        buf = io.StringIO()
        self.ex.writeimage(io.StringIO(val))
        self.ex.readimage(buf)
        self.assertEqual(val, buf.getvalue())

