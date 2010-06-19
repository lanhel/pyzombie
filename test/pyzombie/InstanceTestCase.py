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
from datetime import datetime, timedelta
import unittest
import pyzombie
from pyzombie.Executable import Executable
from pyzombie.Instance import Instance
from pyzombie.ZombieConfig import config, datadir


class InstanceBase(unittest.TestCase):
    def setUp(self):
        self.ex = Executable("testinstance", mediatype="text/x-python")
        self.inst_name = Instance.createname()
        self.inst_dir = os.path.join(self.ex.dirpath, self.inst_name)
        self.inst = Instance(self.ex, self.inst_name)

    def tearDown(self):
        shutil.rmtree(self.ex.dirpath)


class InstancePropertiesTest(InstanceBase):

    def runTest(self):
        self.assertEqual(self.inst_dir, self.inst.datadir)
        self.assertEqual("testinstance", self.ex.name)
        self.assertEqual(os.path.join(self.inst_dir, "var"), self.inst.workdir)
        self.assertEqual(os.path.join(self.inst_dir, "tmp"), self.inst.tmpdir)
        self.assertGreater(self.inst.timeout, datetime.utcnow() + timedelta(seconds=4))
        self.assertGreater(self.inst.remove, datetime.utcnow() + timedelta(days=6))
        self.assertIsNone(self.inst.process)

class InstanceIOTest(InstanceBase):
    def runTest(self):
        pass
        val = "Hello world"


