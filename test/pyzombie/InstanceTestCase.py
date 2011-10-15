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

