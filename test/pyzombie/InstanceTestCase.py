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
from time import sleep
import unittest
import pyzombie
from pyzombie.Executable import Executable
from pyzombie.Instance import Instance
from pyzombie.Instance import DELTA_T
from pyzombie.ZombieConfig import config, datadir
import TestSourceCLI


class InstancePropertiesNoRunTest(unittest.TestCase):
    """Check that properties are correctly initialized for running process."""

    def setUp(self):
        self.ex = Executable(self.__class__.__name__, mediatype="text/x-python")
        self.inst_name = Instance.createname()
        self.inst_dir = os.path.join(self.ex.dirpath, self.inst_name)
        self.inst = Instance(self.ex, self.inst_name)

    def tearDown(self):
        self.ex.delete()

    def runTest(self):
        self.assertEqual(self.inst.datadir, self.inst_dir)
        self.assertEqual(self.ex.name, self.__class__.__name__)
        self.assertEqual(self.inst.workdir, os.path.join(self.inst_dir, "var"))
        self.assertEqual(self.inst.tmpdir, os.path.join(self.inst_dir, "tmp"))
        self.assertGreater(self.inst.timeout, datetime.utcnow() + timedelta(seconds=4))
        self.assertGreater(self.inst.remove, datetime.utcnow() + timedelta(days=6))
        self.assertIsNone(self.inst.process)
        self.assertLess(self.inst.start, datetime.utcnow())
        self.assertIsNone(self.inst.end)
        self.assertIsNone(self.inst.returncode)
        self.assertEqual(self.inst.stdout_path, os.path.join(self.inst_dir, "stdout.txt"))
        self.assertEqual(self.inst.stderr_path, os.path.join(self.inst_dir, "stderr.txt"))
        self.assertIsNotNone(self.inst.stdin)
        self.assertIsNotNone(self.inst.stdout)
        self.assertIsNotNone(self.inst.stderr)


class InstanceCLITest(unittest.TestCase):
    """Check that standard input, output, and error are working properly."""

    def setUp(self):
        self.ex = Executable(self.__class__.__name__, mediatype="text/x-python")
        self.ex.writeimage(open(TestSourceCLI.__file__, "r"))
        self.inst_name = Instance.createname()
        self.inst_dir = os.path.join(self.ex.dirpath, self.inst_name)        
        self.inst = Instance(self.ex, self.inst_name,
                arguments=TestSourceCLI.ARGV, environ=TestSourceCLI.ENVIRON)

    def tearDown(self):
        self.ex.delete()

    def runTest(self):
        self.assertEqual(self.inst.datadir, self.inst_dir)
        self.assertIsNotNone(self.inst.process)
        self.assertLess(self.inst.start, datetime.utcnow())
        self.assertIsNone(self.inst.end)
        self.assertIsNone(self.inst.returncode)
        self.assertEqual(self.inst.stdout_path, os.path.join(self.inst_dir, "stdout.txt"))
        self.assertEqual(self.inst.stderr_path, os.path.join(self.inst_dir, "stderr.txt"))
        self.assertIsNotNone(self.inst.stdin)
        self.assertIsNotNone(self.inst.stdout)
        self.assertIsNotNone(self.inst.stderr)
        
        self.inst.stdin.write(TestSourceCLI.STDIN.encode("UTF-8"))
        self.inst.stdin.flush()
        self.inst.stdin.close()
        self.assertNotEqual(0, self.inst.process.pid, "Process not started.")
        returncode = self.inst.process.wait()
        sleep(DELTA_T)
        TestSourceCLI.validateResults(self,
                "{0}_{1}".format(self.ex.name, self.inst_name),
                self.inst.returncode, self.inst.stdout, self.inst.stderr)

